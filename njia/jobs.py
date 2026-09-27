"""Live, eligibility-filtered job postings matched to confirmed skills.

``POST /api/jobs`` with ``{country, role, skills, source}``; the UI calls it
twice: ``source="remote"`` (Himalayas public API, fast) then ``source="web"``
(Groq browser_search for local postings, slow). Providers only receive the
role, the country and top market skill names from the historical dataset,
never CV text or the user's skills. Web results are kept only when their URL
appears in the search tool's own output. Postings are cached in memory per
(source, country, role); skill matching runs per request and is not cached.
"""
import asyncio
from datetime import datetime, timedelta, timezone
import hashlib
import html
import json
import re
import time
from typing import Annotated, Literal
import unicodedata
from urllib.parse import urlsplit

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from . import engine, groq_client

router = APIRouter()

HIMALAYAS_SEARCH = "https://himalayas.app/jobs/api/search"
HIMALAYAS_TIMEOUT = 12.0
MAX_HIMALAYAS_BYTES = 2 * 1024 * 1024
WEB_TIMEOUT = 45.0
TTL = {"remote": 3600, "web": 3 * 3600}
CACHE_MAX = 64
MAX_JOBS = 8
MAX_WEB_JOBS = 6
MAX_SKILL_TEXT = 6000
MAX_WEB_AGE_DAYS = 120
SOURCES = {
    "remote": [{"name": "Himalayas", "url": "https://himalayas.app"}],
    "web": [{"name": "Groq browser search", "url": "https://console.groq.com/docs/browser-search"}],
}
COMMON_NOTES = [
    "Live postings change quickly. Confirm the details, deadline and eligibility on the source site before applying.",
    "Match % is the share of skills we detected in the posting that are in your confirmed list. It is not a hiring probability.",
]
SENIOR = {"Senior", "Manager", "Director", "Executive"}
JUNIOR = {"Entry-level", "Mid-level"}
ANALYST_EXCLUDE = r"behaviou?r|bcba|\brbt\b|\baba\b|therap|analyst relations|clinical|nurs|sales rep|recruit"
TECH_EXCLUDE = r"\bsales\b|recruit|customer support|support engineer|mechanical|civil|electrical|chemical|hvac|field service"
ROLES = {
    "Data Analyst": ("data analyst", r"\b(?:data|bi|business intelligence|analytics|reporting|insights?|dashboards?|sql|tableau|power bi|metrics|quantitative|statistic\w*)\b", r"\b(?:analyst|analytics|insights?)\b", ANALYST_EXCLUDE),
    "Senior Data Analyst": ("data analyst", r"\b(?:data|bi|business intelligence|analytics|reporting|insights?|dashboards?|sql|tableau|power bi|metrics|quantitative|statistic\w*)\b", r"\b(?:analyst|analytics|insights?)\b", ANALYST_EXCLUDE),
    "Business Analyst": ("business analyst", r"\b(?:business|systems?|process|functional|product|requirements|operations|erp|crm|data|bi)\b", r"\b(?:analyst|analysis)\b", ANALYST_EXCLUDE),
    "Data Engineer": ("data engineer", r"\b(?:data|etl|elt|analytics|pipelines?|big data|warehouse|lakehouse|databricks|spark|dwh)\b", r"\b(?:engineer|engineering|developer|architect)\b", TECH_EXCLUDE),
    "Senior Data Engineer": ("data engineer", r"\b(?:data|etl|elt|analytics|pipelines?|big data|warehouse|lakehouse|databricks|spark|dwh)\b", r"\b(?:engineer|engineering|developer|architect)\b", TECH_EXCLUDE),
    "Data Scientist": ("data scientist", r"\b(?:data|machine learning|ml|ai|applied|decision|statistic\w*|quantitative|analytics)\b", r"\b(?:scien\w*|statistician|modell?er|machine learning)\b", r"clinical|chemist|biolog|laborator|\blab\b|neuro|" + ANALYST_EXCLUDE),
    "Senior Data Scientist": ("data scientist", r"\b(?:data|machine learning|ml|ai|applied|decision|statistic\w*|quantitative|analytics)\b", r"\b(?:scien\w*|statistician|modell?er|machine learning)\b", r"clinical|chemist|biolog|laborator|\blab\b|neuro|" + ANALYST_EXCLUDE),
    "Software Engineer": ("software engineer", r"\b(?:software|backend|back-end|frontend|front-end|full[- ]?stack|web|mobile|python|java|javascript|typescript|node(?:\.js)?|react|golang|go|ruby|php|\.net|c#|android|ios|platform|application|api)\b", r"\b(?:engineer|developer|programmer|swe)\b", TECH_EXCLUDE),
    "Cloud Engineer": ("cloud engineer", r"\b(?:cloud|aws|azure|gcp|devops|sre|site reliability|platform|infrastructure|kubernetes|devsecops)\b", r"\b(?:engineer|architect|developer|specialist|administrator|consultant)\b", TECH_EXCLUDE),
    "Machine Learning Engineer": ("machine learning engineer", r"\b(?:machine learning|ml|mlops|ai|deep learning|computer vision|nlp|llms?|genai|generative ai)\b", r"\b(?:engineer|developer|scientist|researcher|architect)\b", TECH_EXCLUDE + r"|trainer|tutor|annotat|label?ling|rater"),
}
BOARDS = {
    "Kenya": "brightermonday.co.ke, fuzu.com, myjobmag.co.ke, linkedin.com/jobs, ke.indeed.com",
    "Nigeria": "jobberman.com, myjobmag.com, linkedin.com/jobs, ng.indeed.com",
    "South Africa": "pnet.co.za, careers24.com, linkedin.com/jobs, za.indeed.com",
    "Egypt": "wuzzuf.net, bayt.com, linkedin.com/jobs",
    "Morocco": "rekrute.com, emploi.ma, linkedin.com/jobs",
    "Saudi Arabia": "bayt.com, linkedin.com/jobs, sa.indeed.com",
}
# Pages that are never individual postings: profiles, social posts, search/category pages.
NOT_POSTING = re.compile(r"^https://(?:[\w-]+\.)?(?:exa\.ai|facebook\.com|twitter\.com|x\.com|instagram\.com|youtube\.com|tiktok\.com|himalayas\.app)/"
                         r"|^https://(?:[\w-]+\.)?linkedin\.com/(?!jobs/view/)|/(?:search|in|people|profile|company|companies)(?:/|$|\?)|[?&](?:q|query|keywords?)=", re.I)
LISTING_TITLE = re.compile(r"\bjobs\b|\bvacancies\b|\bjob openings\b|\bsearch\b|\bresults\b|you do not have access|page not found|\berror\b", re.I)
CLOSED = re.compile(r"\b(?:this job has expired|job (?:has )?expired|no longer (?:available|accepting)|applications? (?:are |is )?closed|position (?:has been )?filled)\b", re.I)
COUNTRY_ALIASES = {"cote d'ivoire": {"ivory coast", "cote divoire"}}
PERIODS = {"hourly": "hour", "weekly": "week", "fortnightly": "fortnight", "monthly": "month", "annual": "year", "yearly": "year"}

_cache: dict = {}
_inflight: dict = {}


class JobsRequest(BaseModel):
    country: str = Field(max_length=80)
    role: str = Field(max_length=80)
    skills: list[Annotated[str, Field(max_length=80)]] = Field(default_factory=list, max_length=100)
    source: Literal["remote", "web"] = "remote"


def _fold(text) -> str:
    text = unicodedata.normalize("NFKD", str(text or "").replace("’", "'")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", text).strip().lower()


def _country_names(country):
    base = _fold(country)
    return {base, *COUNTRY_ALIASES.get(base, set())}


def _clean(value, limit=200):
    if not isinstance(value, str):
        return None
    value = re.sub(r"\s+", " ", html.unescape(value)).strip()
    return value[:limit] or None


def _html_text(value) -> str:
    text = re.sub(r"<[^>]+>", "\n", value) if isinstance(value, str) else ""
    return html.unescape(text)


def relevant(role: str, title: str) -> bool:
    _, topic, noun, exclude = ROLES[role]
    title = _fold(title)
    return bool(title and re.search(topic, title) and re.search(noun, title) and not re.search(exclude, title))


def job_skills(*parts) -> list[str]:
    text = "\n".join(p for p in parts if isinstance(p, str))[:MAX_SKILL_TEXT * 2]
    # Job prose trips the CV-oriented negation guard ("machine learning, Python"), so split clauses first.
    text = re.sub(r"\b(?:[A-Z]&[A-Z]|C-(?:level|suite)|Series [A-F])\b", " ", text)
    text = re.sub(r"[,•·|/()]+|\s(?:and|or)\s", "\n", text)
    return engine.extract_skills(text)


def eligibility(restrictions, country):
    if not isinstance(restrictions, list):
        return None
    names = [_fold(r) for r in restrictions if isinstance(r, str) and r.strip()]
    if not names:
        return "Open worldwide"
    if not _country_names(country) & set(names):
        return None
    others = len(set(names)) - 1
    return f"Open to {country}" + (f" + {others} more {'country' if others == 1 else 'countries'}" if others else " only")


def salary(job):
    low, high = job.get("minSalary"), job.get("maxSalary")
    numbers = [n for n in (low, high) if isinstance(n, (int, float)) and not isinstance(n, bool) and n > 0]
    if not numbers:
        return None
    low, high = min(numbers), max(numbers)
    amount = f"{low:,.0f}" if low == high else f"{low:,.0f}–{high:,.0f}"
    currency = job.get("currency") if isinstance(job.get("currency"), str) and re.fullmatch(r"[A-Z]{3}", job.get("currency") or "") else ""
    period = PERIODS.get(str(job.get("salaryPeriod") or "").lower())
    return " ".join(p for p in (currency, amount) if p) + (f" / {period}" if period else "")


def _iso_date(timestamp):
    if isinstance(timestamp, (int, float)) and not isinstance(timestamp, bool) and timestamp > 0:
        try:
            return datetime.fromtimestamp(timestamp, tz=timezone.utc).date().isoformat()
        except (OverflowError, OSError, ValueError):
            return None
    return None


def _job_id(url):
    return hashlib.sha256(url.encode()).hexdigest()[:12]


def _cache_get(key):
    entry = _cache.get(key)
    if entry and entry[0] > time.monotonic():
        return entry[1]
    _cache.pop(key, None)
    return None


def _cache_put(key, value):
    _cache[key] = (time.monotonic() + TTL[key[0]], value)
    while len(_cache) > CACHE_MAX:
        _cache.pop(min(_cache, key=lambda k: _cache[k][0]))


def _settle(key, task):
    if _inflight.get(key) is task:
        _inflight.pop(key, None)
    if not task.cancelled():
        task.exception()  # mark retrieved; each waiter handles it


async def _shared_fetch(key):
    """One provider call per (source, country, role) at a time; concurrent requests await the same
    task, which keeps running (and fills the cache) if a browser aborts."""
    task = _inflight.get(key)
    if task is None or task.get_loop() is not asyncio.get_running_loop():
        async def run():
            result = await (fetch_remote if key[0] == "remote" else fetch_web)(key[1], key[2])
            _cache_put(key, result)
            return result
        task = asyncio.ensure_future(run())
        _inflight[key] = task
        task.add_done_callback(lambda t: _settle(key, t))
    return await asyncio.shield(task)


async def _get_json(url, params):
    async with asyncio.timeout(HIMALAYAS_TIMEOUT):
        async with httpx.AsyncClient(timeout=HIMALAYAS_TIMEOUT, trust_env=False, follow_redirects=False) as client:
            async with client.stream("GET", url, params=params, headers={"Accept": "application/json", "User-Agent": "Njia career coach"}) as response:
                response.raise_for_status()
                body = bytearray()
                async for chunk in response.aiter_bytes():
                    if len(body) + len(chunk) > MAX_HIMALAYAS_BYTES:
                        raise ValueError("Response too large")
                    body.extend(chunk)
    return json.loads(bytes(body))


async def fetch_remote(country, role):
    """Normalized Himalayas postings open to ``country`` and relevant to ``role``."""
    query = ROLES[role][0]
    data = await _get_json(HIMALAYAS_SEARCH, {"q": query, "country": country, "limit": 20})
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise ValueError("Unexpected Himalayas response")
    now, jobs, seen = time.time(), [], set()
    for raw in data["jobs"][:20]:
        if not isinstance(raw, dict):
            continue
        title, url = _clean(raw.get("title")), raw.get("applicationLink") or raw.get("guid")
        normal = groq_client.normalize_url(url)
        expiry = raw.get("expiryDate")
        if not title or not normal or not normal.startswith("https://himalayas.app/") or not relevant(role, title):
            continue
        if isinstance(expiry, (int, float)) and not isinstance(expiry, bool) and 0 < expiry < now:
            continue
        where = eligibility(raw.get("locationRestrictions", []), country)
        if where is None or normal in seen:
            continue
        seen.add(normal)
        seniority = [s for s in raw.get("seniority") or [] if isinstance(s, str)][:4] if isinstance(raw.get("seniority"), list) else []
        pub = raw.get("pubDate") if isinstance(raw.get("pubDate"), (int, float)) else 0
        jobs.append({
            "id": _job_id(normal), "title": title, "company": _clean(raw.get("companyName"), 120),
            "location": "Remote" if where == "Open worldwide" else f"Remote · {country}", "eligibility": where,
            "url": url.strip(), "source": "Himalayas", "kind": "remote", "posted": _iso_date(raw.get("pubDate")),
            "seniority": seniority, "employment_type": _clean(raw.get("employmentType"), 40), "salary": salary(raw),
            "_skills": job_skills(title, _clean(raw.get("excerpt"), 1000) or "", _html_text(raw.get("description"))[:MAX_SKILL_TEXT]),
            "_ts": float(pub),
        })
    total = data.get("totalCount") if isinstance(data.get("totalCount"), int) and not isinstance(data.get("totalCount"), bool) else None
    return {"jobs": jobs, "total_available": total, "query": query, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def _web_messages(country, role):
    skills = ", ".join(s["label"] for s in engine.market(country, role)["skills"][:5])
    boards = BOARDS.get(country, "linkedin.com/jobs, indeed.com and local job boards")
    today = datetime.now(timezone.utc).date().isoformat()
    return [
        {"role": "system", "content": "You find currently open job postings with web search. Use only postings you found in search results or opened pages. Never invent or guess URLs, companies or dates. Reply with one JSON object only."},
        {"role": "user", "content": (
            f"Today is {today}. Search the web for up to {MAX_WEB_JOBS} currently open {role} job postings located in {country} (on-site or hybrid), "
            f"for example on {boards} or company career pages. Relevant skills: {skills}. "
            "Open promising individual posting pages to confirm they are current. Skip profiles, category pages and search pages. "
            "Copy each URL exactly as it appears in the search results. "
            'Return JSON: {"jobs":[{"title":"","company":"","location":"","url":"","posted":"YYYY-MM-DD or null","source":"site name","requirements":["short requirement"]}]}. '
            'Use {"jobs":[]} if you find none.'
        )},
    ]


def _posted_from_text(text, now=None):
    """Best-effort posting date from an opened page's visible text (first lines only)."""
    now = now or datetime.now(timezone.utc)
    head = text[:1500]
    found = re.search(r"\b(?:posted:?\s*)?(today|yesterday|(\d{1,2})\s+(hour|day|week|month)s?\s+ago)\b", head, re.I)
    if found:
        word = found.group(1).lower()
        if word == "today" or (found.group(3) or "").lower() == "hour":
            days = 0
        elif word == "yesterday":
            days = 1
        else:
            days = int(found.group(2)) * {"day": 1, "week": 7, "month": 30}[found.group(3).lower()]
        return (now - timedelta(days=days)).date().isoformat()
    found = re.search(r"\bposted:?\s*([A-Z][a-z]{2,8} \d{1,2}, 20\d\d)\b", head)
    if found:
        for fmt in ("%b %d, %Y", "%B %d, %Y"):
            try:
                return datetime.strptime(found.group(1), fmt).date().isoformat()
            except ValueError:
                continue
    return None


def _split_title(raw):
    """'Data Analyst at Acme | BrighterMonday' -> ('Data Analyst', 'Acme', 'BrighterMonday')."""
    text = re.sub(r"\\\|", "|", raw or "").strip()
    parts = [p.strip() for p in re.split(r"\s+[|–—]\s+", text) if p.strip()]
    board = parts[-1] if len(parts) > 1 else None
    head = parts[0] if parts else ""
    title, _, company = head.rpartition(" at ") if " at " in head else (head, "", "")
    company = re.sub(r",?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+20\d\d$", "", company)
    return _clean(title), _clean(company, 120), _clean(board, 60)


def _opened_pages(message):
    """Pages the search tool actually opened: {normalized url: (url, title line, text)} straight from tool output."""
    pages = {}
    tools = message.get("executed_tools") if isinstance(message, dict) else None
    for tool in tools if isinstance(tools, list) else []:
        if not isinstance(tool, dict) or tool.get("name") != "browser.open" or not isinstance(tool.get("output"), str):
            continue
        text = re.sub(r"(?m)^L\d+: ?", "", tool["output"])
        found = re.search(r"URL:\s*(https?://\S+)\s*\n\s*(.+)", text)
        if not found or LISTING_TITLE.search(found.group(2)) or CLOSED.search(text[:4000]):
            continue
        normal = groq_client.normalize_url(found.group(1))
        if normal and not NOT_POSTING.search(normal):
            pages.setdefault(normal, (found.group(1), found.group(2), text[found.end():found.end() + MAX_SKILL_TEXT]))
    return pages


def _web_job(country, url, normal, title, company, location, source, posted, skill_text):
    ts = 0.0
    if posted:
        try:
            ts = datetime.fromisoformat(posted).replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            posted = None
    age_days = (time.time() - ts) / 86400 if posted else None
    if age_days is not None and age_days < -1:
        posted, ts = None, 0.0  # a future date is not credible
    elif age_days is not None and age_days > MAX_WEB_AGE_DAYS:
        return None  # likely closed; do not present as open
    return {
        "id": _job_id(normal), "title": title, "company": company, "location": location or country,
        "eligibility": f"Local posting · {country}", "url": url.strip().rstrip(".,;:!?)]}'\""), "source": source or "Web search",
        "kind": "local", "posted": posted, "seniority": [], "employment_type": None, "salary": None,
        "_skills": job_skills(title, *skill_text), "_ts": ts,
    }


async def fetch_web(country, role):
    """Local postings found by Groq browser_search. A posting is kept only if its URL is in the
    tool's own output: either a page the tool opened, or a model-listed URL present in the evidence."""
    content, message, _ = await groq_client.chat(_web_messages(country, role), json_mode=False, tools=groq_client.BROWSER_SEARCH,
                                                  max_tokens=4000, timeout=WEB_TIMEOUT, model=groq_client.search_model())
    evidence = groq_client.evidence_urls(message)
    pages = _opened_pages(message)
    try:
        data = groq_client.loose_json(content)
    except ValueError:
        data = {}
    items = data.get("jobs") if isinstance(data.get("jobs"), list) else []
    jobs, seen, dropped = [], set(), 0
    for raw in items[:12]:
        if not isinstance(raw, dict):
            continue
        title, url = _clean(raw.get("title")), raw.get("url")
        normal = groq_client.normalize_url(url)
        if not title or not normal or normal in seen or NOT_POSTING.search(normal) or not relevant(role, title):
            continue
        if normal not in evidence:
            dropped += 1
            continue
        seen.add(normal)
        posted = raw.get("posted").strip() if isinstance(raw.get("posted"), str) and re.fullmatch(r"\s*20\d\d-\d\d-\d\d\s*", raw.get("posted")) else None
        requirements = [r for r in (_clean(x, 200) for x in (raw.get("requirements") or [])[:12]) if r] if isinstance(raw.get("requirements"), list) else []
        page = pages.get(normal)
        if page:
            posted = _posted_from_text(page[2]) or posted
        jobs.append(_web_job(country, url, normal, title, _clean(raw.get("company"), 120), _clean(raw.get("location"), 120),
                             _clean(raw.get("source"), 60), posted, [*requirements, page[2] if page else ""]))
    for normal, (url, heading, text) in pages.items():
        title, company, board = _split_title(heading)
        if normal in seen or not title or not relevant(role, title):
            continue
        seen.add(normal)
        jobs.append(_web_job(country, url, normal, title, company, None, board or urlsplit(normal).hostname, _posted_from_text(text), [text]))
    same = set()
    unique = []
    for job in jobs:
        if job is None:
            continue
        key = (_fold(job["title"]), _fold(job["company"]))
        if job["company"] and key in same:
            continue
        same.add(key)
        unique.append(job)
    return {"jobs": unique[:MAX_WEB_JOBS], "total_available": None, "dropped": dropped, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def match(job, role, skills, order):
    """Per-request comparison of a posting's detected skills with the user's confirmed skills."""
    detected = job["_skills"]
    rank = lambda s: (order.get(s, len(order)), s)
    matched = sorted((s for s in detected if s in skills), key=rank)
    missing = sorted((s for s in detected if s not in skills), key=rank)
    levels = set(job["seniority"])
    fit = not levels or bool(levels & (SENIOR if role.startswith("Senior") else JUNIOR))
    pct = round(100 * len(matched) / len(detected)) if detected else None
    public = {k: v for k, v in job.items() if not k.startswith("_")}
    # Rank with +1 smoothing so a 1-of-1 match does not outrank 3 of 4; seniority mismatch ranks lower.
    score = 100 * len(matched) / (len(detected) + 1) - (0 if fit else 25)
    return {**public, "match_pct": pct, "matched_skills": matched, "missing_skills": missing[:10], "detected_count": len(detected),
            "seniority_fit": fit}, (score, job["_ts"])


def validate(body: JobsRequest):
    meta = engine.metadata()
    if body.country not in {c["name"] for c in meta["countries"]} or body.role not in meta["roles"] or body.role not in ROLES:
        raise HTTPException(422, "Choose a country and role from the available dataset.")
    vocabulary = set(engine.vocabulary())
    if any(s not in vocabulary for s in body.skills):
        raise HTTPException(422, "One or more skills are outside the dataset vocabulary.")
    return set(body.skills)


@router.post("/api/jobs")
async def live_jobs(body: JobsRequest):
    skills = validate(body)
    key = (body.source, body.country, body.role)
    notes = list(COMMON_NOTES)
    notes.append("Eligibility comes from each listing's location restrictions on Himalayas. Employers may add time-zone or work-permit requirements."
                 if body.source == "remote" else
                 "Found via web search · verify on source. Only postings whose links appeared in the search tool's own results are shown.")
    result = _cache_get(key)
    cached = result is not None
    if not cached:
        try:
            if body.source == "web" and not groq_client.configured():
                raise LookupError("Web search is not configured")
            result = await _shared_fetch(key)
        except LookupError:
            return _empty(body.source, notes, "not_configured", "Local web search is not configured on this server, so only remote listings are shown.")
        except (groq_client.ProviderError, httpx.HTTPError, TimeoutError, ValueError, TypeError, KeyError, RecursionError, UnicodeDecodeError):
            name = "Himalayas" if body.source == "remote" else "Web search"
            return _empty(body.source, notes, "unavailable", f"{name} could not be reached or returned an unusable response. Try again in a minute.")
    order = {s["id"]: i for i, s in enumerate(engine.market(body.country, body.role)["skills"])}
    ranked = sorted((match(job, body.role, skills, order) for job in result["jobs"]), key=lambda pair: pair[1], reverse=True)
    if body.source == "web" and result.get("dropped"):
        notes.append(f"{result['dropped']} search result(s) were hidden because their links could not be verified in the search output.")
    if not skills:
        notes.append("Confirm your skills to see how you match each posting.")
    return {"source": body.source, "jobs": [job for job, _ in ranked[:MAX_JOBS]], "total_available": result.get("total_available"),
            "query": result.get("query"), "fetched_at": result["fetched_at"], "cached": cached, "status": "ok", "message": None,
            "sources": SOURCES[body.source], "notes": notes}


def _empty(source, notes, status, message):
    """Provider failures still answer 200 so the rest of the brief renders; bodies are never echoed."""
    return {"source": source, "jobs": [], "total_available": None, "query": None,
            "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "cached": False,
            "status": status, "message": message, "sources": SOURCES[source], "notes": [*notes, message]}
