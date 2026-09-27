"""Deterministic demand calculations and local TF-IDF job retrieval.

CVs and results are request-scoped; only the public job corpus is cached.
"""
from collections import Counter
from functools import lru_cache
import json
from pathlib import Path
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

ROOT = Path(__file__).resolve().parent.parent
MIN_LOCAL_POSTINGS = 50
ALIASES = {
    "power bi": ["powerbi", "power-bi"],
    "excel": ["microsoft excel", "ms excel"],
    "sql": ["structured query language"],
    "javascript": ["js", "java script"],
    "typescript": ["ts"],
    "postgresql": ["postgres"],
    "aws": ["amazon web services"],
    "gcp": ["google cloud", "google cloud platform"],
    "azure": ["microsoft azure"],
    "c++": ["cpp"],
    "c#": ["c sharp", "csharp"],
    "node.js": ["nodejs", "node js"],
    "scikit-learn": ["sklearn", "scikit learn"],
    "pytorch": ["py torch"],
    "tensorflow": ["tensor flow"],
    "kubernetes": ["k8s"],
    "r": ["r programming", "r language", "r studio", "rstudio"],
    "powerpoint": ["power point"],
}
DISPLAY = {"sql": "SQL", "r": "R", "aws": "AWS", "gcp": "Google Cloud", "power bi": "Power BI", "spss": "SPSS", "sas": "SAS", "c++": "C++", "c#": "C#", "javascript": "JavaScript", "postgresql": "PostgreSQL", "pytorch": "PyTorch", "tensorflow": "TensorFlow", "scikit-learn": "scikit-learn", "github": "GitHub", "node.js": "Node.js"}


def display(skill: str) -> str:
    return DISPLAY.get(skill, skill.title())


@lru_cache(maxsize=1)
def corpus():
    with (ROOT / "data/africa_jobs_subset.jsonl").open(encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    alias_map = {alias: canonical for canonical, aliases in ALIASES.items() for alias in aliases}
    for row in rows:
        row["skills"] = sorted({alias_map.get(s.lower(), s.lower()) for s in row["skills"]})
    return rows


@lru_cache(maxsize=1)
def vocabulary():
    return sorted({skill.lower() for row in corpus() for skill in row["skills"]})


def scrub_pii(text: str) -> str:
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", "[email removed]", text)
    text = re.sub(r"(?<!\w)\+?\d[\d ()-]{7,}\d(?!\w)", "[number removed]", text)
    text = re.sub(r"https?://\S+|www\.\S+", "[link removed]", text)
    # Remove explicit identity lines. This is best-effort, not full anonymization.
    text = re.sub(r"(?im)^\s*(?:name|nom|jina|address|adresse|national id|passport)\s*:.*$", "[identity removed]", text)
    return text


def extract_skills(text: str) -> list[str]:
    """Conservative lexicon extraction. Suggestions always remain user-editable."""
    text = scrub_pii(text)
    found = set()
    for skill in vocabulary():
        for alias in [skill, *ALIASES.get(skill, [])]:
            # Single-letter names are ambiguous in prose; only accept uppercase.
            flags = 0 if len(alias) == 1 else re.IGNORECASE
            needle = alias.upper() if len(alias) == 1 else alias
            for match in re.finditer(r"(?<![\w+#])" + re.escape(needle) + r"(?![\w+#])", text, flags):
                prefix = re.split(r"[.\n;:]", text[:match.start()])[-1].lower()
                if re.search(r"\b(?:no|not|never|without|lack|lacking|learning|learn|want|aspire|sans|aucune?|apprendre|sijui|kujifunza)\b", prefix):
                    continue
                # Ordinary verbs/nouns would otherwise create spurious skills.
                if skill in {"go", "flow", "word", "sheets", "windows", "outlook"}:
                    nearby = text[max(0, match.start()-25):match.end()+20].lower()
                    if skill == "go" and not re.search(r"golang|go (?:programming|language|developer)|(?:skills|stack|languages)\s*:", nearby):
                        continue
                    if skill == "flow" and "power automate" not in nearby:
                        continue
                    if skill in {"word", "sheets", "outlook"} and not re.search(r"microsoft|google|ms |skills\s*:", nearby):
                        continue
                found.add(skill)
    return sorted(found)


def metadata():
    rows = corpus()
    counts = Counter(r["job_country"] for r in rows)
    return {
        "countries": [{"name": c, "postings": counts[c]} for c in sorted(counts)],
        "roles": sorted({r["job_title_short"] for r in rows}),
        "skills": [{"id": s, "label": display(s)} for s in vocabulary()],
        "postings": len(rows), "year": 2023,
        "source": "lukebarousse/data_jobs",
        "source_url": "https://huggingface.co/datasets/lukebarousse/data_jobs",
        "minimum_local_postings": MIN_LOCAL_POSTINGS,
    }


@lru_cache(maxsize=100)
def market(country: str, role: str):
    role_rows = [r for r in corpus() if r["job_title_short"] == role]
    local_rows = [r for r in role_rows if r["job_country"] == country]
    fallback = len(local_rows) < MIN_LOCAL_POSTINGS
    rows = role_rows if fallback else local_rows
    counts = Counter(s for row in rows for s in set(row["skills"]))
    top = sorted(counts.items(), key=lambda p: (-p[1], p[0]))[:15]
    return {
        "country": country, "role": role, "local_postings": len(local_rows),
        "sample_size": len(rows), "fallback": fallback,
        "scope": "10-country Africa/MENA sample" if fallback else country,
        "skills": [{"id": s, "label": display(s), "count": n, "demand_pct": round(n / len(rows) * 100, 1)} for s, n in top],
    }


@lru_cache(maxsize=100)
def retrieval_index(country: str, role: str):
    info = market(country, role)
    rows = [r for r in corpus() if r["job_title_short"] == role and (info["fallback"] or r["job_country"] == country)]
    vectorizer = TfidfVectorizer(tokenizer=str.split, token_pattern=None, lowercase=False)
    matrix = vectorizer.fit_transform([" ".join(s.replace(" ", "_") for s in r["skills"]) for r in rows])
    return rows, vectorizer, matrix


def related_jobs(country: str, role: str, skills: list[str]):
    if not skills:
        return []
    rows, vectorizer, matrix = retrieval_index(country, role)
    query = vectorizer.transform([" ".join(s.replace(" ", "_") for s in skills)])
    scores = linear_kernel(query, matrix).ravel()
    results, seen = [], set()
    for idx in scores.argsort()[::-1]:
        if scores[idx] <= 0 or len(results) == 3:
            break
        row = rows[idx]
        identity = (row["job_title"], tuple(sorted(row["skills"])))
        if identity in seen:
            continue
        seen.add(identity)
        results.append({"title": row["job_title"], "country": row["job_country"], "similarity": round(float(scores[idx]), 3), "skills": [display(s) for s in row["skills"]], "matched": [display(s) for s in row["skills"] if s in skills]})
    return results


def analyze(country: str, role: str, skills: list[str]):
    info = market(country, role)
    total = sum(s["count"] for s in info["skills"])
    matched = sum(s["count"] for s in info["skills"] if s["id"] in skills)
    demand = [{**s, "owned": s["id"] in skills} for s in info["skills"]]
    return {
        **info, "skills": demand, "confirmed_skills": skills,
        "coverage": round(100 * matched / total, 1) if total else 0,
        "matched_count": sum(s["owned"] for s in demand),
        "gaps": [s for s in demand if not s["owned"]],
        "jobs": related_jobs(country, role, skills),
        "method": "Demand-weighted coverage of the top 15 skills; not a probability of employment or a verified proficiency score.",
        "retrieval_method": "Local TF-IDF + cosine similarity over posting skills. Historical examples, not open vacancies.",
    }
