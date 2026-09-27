import asyncio
import json
import os
import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
import httpx

from njia.app import app
from njia import jobs

NOW = int(time.time())


def posting(title, restrictions=(), description="", seniority=("Mid-level",), expires=NOW + 86400, published=NOW - 3600, slug=None):
    slug = slug or title.lower().replace(" ", "-").replace("(", "").replace(")", "")
    return {"title": title, "companyName": "Acme", "companySlug": "acme", "locationRestrictions": list(restrictions),
            "seniority": list(seniority), "pubDate": published, "expiryDate": expires, "excerpt": "",
            "description": description, "employmentType": "Full Time", "minSalary": None, "maxSalary": None,
            "currency": None, "salaryPeriod": "annual", "applicationLink": f"https://himalayas.app/companies/acme/jobs/{slug}"}


def groq_envelope(content, tools):
    return {"model": "openai/gpt-oss-20b", "choices": [{"finish_reason": "stop", "message": {
        "role": "assistant", "content": content, "executed_tools": tools}}]}


class LiveJobsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.client_class = httpx.AsyncClient

    def setUp(self):
        jobs._cache.clear()
        self.calls = []
        self.payload = {"country": "Kenya", "role": "Data Analyst", "skills": ["sql", "excel"], "source": "remote"}
        self.himalayas = {"totalCount": 111, "jobs": []}
        self.groq = None
        self.environment = patch.dict(os.environ, {"GROQ_API_KEY": "jobs-test-secret", "GROQ_MODEL": "", "NJIA_ADVISOR_MODEL": ""})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def handler(self, request):
        self.calls.append(request)
        if request.url.host == "himalayas.app":
            if isinstance(self.himalayas, int):
                return httpx.Response(self.himalayas, text="PROVIDER-SECRET-BODY")
            return httpx.Response(200, json=self.himalayas)
        if request.url.host == "api.groq.com":
            if self.groq is None:
                return httpx.Response(503, text="PROVIDER-SECRET-BODY")
            return httpx.Response(200, json=self.groq)
        raise AssertionError(f"Unexpected network call to {request.url.host}")

    def post(self, **changes):
        with patch("njia.jobs.httpx.AsyncClient", side_effect=lambda **kwargs: self.client_class(
                transport=httpx.MockTransport(self.handler), **kwargs)):
            return self.client.post("/api/jobs", json={**self.payload, **changes})

    def test_eligibility_filter_and_expired_postings(self):
        self.himalayas["jobs"] = [
            posting("Data Analyst", description="<p>SQL and Excel</p>", slug="worldwide"),
            posting("BI Analyst", restrictions=["Kenya", "Uganda", "Ghana"], slug="kenya"),
            posting("Reporting Analyst", restrictions=["kenya"], slug="kenya-only"),
            posting("Data Analyst", restrictions=["Nigeria", "Ghana"], slug="other-country"),
            posting("Insights Analyst", expires=NOW - 60, slug="expired"),
        ]
        response = self.post()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        by_url = {job["url"].rsplit("/", 1)[-1]: job for job in data["jobs"]}
        self.assertEqual(set(by_url), {"worldwide", "kenya", "kenya-only"})
        self.assertEqual(by_url["worldwide"]["eligibility"], "Open worldwide")
        self.assertEqual(by_url["kenya"]["eligibility"], "Open to Kenya + 2 more countries")
        self.assertEqual(by_url["kenya-only"]["eligibility"], "Open to Kenya only")
        self.assertEqual(data["total_available"], 111)
        self.assertEqual(data["sources"][0]["name"], "Himalayas")
        self.assertTrue(all(job["kind"] == "remote" and job["source"] == "Himalayas" for job in data["jobs"]))
        request = self.calls[0]
        self.assertEqual(request.url.params["country"], "Kenya")
        self.assertEqual(request.url.params["q"], "data analyst")

    def test_accented_country_eligibility(self):
        self.himalayas["jobs"] = [posting("Data Analyst", restrictions=["Cote d'Ivoire", "Senegal"])]
        data = self.post(country="Côte d'Ivoire").json()
        self.assertEqual([job["eligibility"] for job in data["jobs"]], ["Open to Côte d'Ivoire + 1 more country"])

    def test_relevance_filter_excludes_embarrassing_titles(self):
        self.himalayas["jobs"] = [posting("Behavior Analyst (BCBA)"), posting("Registered Behavior Technician RBT Analyst"),
                                  posting("Senior Communications Manager - Analyst Relations"), posting("Financial Analyst"),
                                  posting("Junior Data Analyst")]
        data = self.post().json()
        self.assertEqual([job["title"] for job in data["jobs"]], ["Junior Data Analyst"])
        self.assertTrue(jobs.relevant("Machine Learning Engineer", "Senior ML Engineer"))
        self.assertFalse(jobs.relevant("Machine Learning Engineer", "AI Trainer"))
        self.assertFalse(jobs.relevant("Data Scientist", "Clinical Research Scientist"))
        self.assertEqual(set(jobs.ROLES), set(jobs.engine.metadata()["roles"]))

    def test_skill_matching_and_ranking(self):
        self.himalayas["jobs"] = [
            posting("Data Analyst", description="<ul><li>Python</li><li>Tableau</li><li>SQL</li></ul>", slug="one-third", published=NOW - 100),
            posting("BI Analyst", description="<p>Excel, SQL and Tableau dashboards</p>", slug="two-thirds", published=NOW - 5000),
            posting("Reporting Analyst", description="<p>Strong communicator.</p>", slug="none-detected"),
            posting("Senior Data Analyst", description="<p>SQL, Excel, Tableau</p>", seniority=["Senior"], slug="senior"),
        ]
        data = self.post().json()
        order = [job["url"].rsplit("/", 1)[-1] for job in data["jobs"]]
        # Senior posting (2 of 3) is penalised for a non-senior target and ties with the newer 1-of-3 posting.
        self.assertEqual(order, ["two-thirds", "one-third", "senior", "none-detected"])
        by_url = {job["url"].rsplit("/", 1)[-1]: job for job in data["jobs"]}
        self.assertEqual(by_url["two-thirds"]["match_pct"], 67)
        self.assertEqual(by_url["two-thirds"]["matched_skills"], ["excel", "sql"])
        self.assertEqual(by_url["two-thirds"]["missing_skills"], ["tableau"])
        self.assertEqual(by_url["one-third"]["match_pct"], 33)
        self.assertEqual(by_url["one-third"]["missing_skills"], ["python", "tableau"])  # ordered by market demand
        self.assertIsNone(by_url["none-detected"]["match_pct"])
        self.assertFalse(by_url["senior"]["seniority_fit"])
        self.assertIn("not a hiring probability", " ".join(data["notes"]))

    def test_cache_hit_avoids_second_fetch_but_rematches_skills(self):
        self.himalayas["jobs"] = [posting("Data Analyst", description="<p>SQL and Python</p>")]
        first = self.post().json()
        second = self.post(skills=["python", "sql"]).json()
        self.assertEqual(len(self.calls), 1)
        self.assertFalse(first["cached"])
        self.assertTrue(second["cached"])
        self.assertEqual(first["jobs"][0]["match_pct"], 50)
        self.assertEqual(second["jobs"][0]["match_pct"], 100)

    def test_concurrent_requests_share_one_provider_call(self):
        self.himalayas["jobs"] = [posting("Data Analyst", description="<p>SQL</p>")]

        async def both():
            first = jobs.JobsRequest(**self.payload)
            second = jobs.JobsRequest(**{**self.payload, "skills": []})
            return await asyncio.gather(jobs.live_jobs(first), jobs.live_jobs(second))

        with patch("njia.jobs.httpx.AsyncClient", side_effect=lambda **kwargs: self.client_class(
                transport=httpx.MockTransport(self.handler), **kwargs)):
            first, second = asyncio.run(both())
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(first["jobs"][0]["match_pct"], 100)
        self.assertEqual(second["jobs"][0]["match_pct"], 0)
        self.assertEqual(jobs._inflight, {})

    def test_validation_errors(self):
        for changes in ({"country": "Atlantis"}, {"role": "Astronaut"}, {"skills": ["not-a-skill"]},
                        {"source": "everything"}, {"skills": ["sql"] * 101}):
            with self.subTest(changes=changes):
                self.assertEqual(self.post(**changes).status_code, 422)
        self.assertEqual(self.calls, [])

    def test_source_failure_returns_empty_with_note_and_is_not_cached(self):
        self.himalayas = 500
        response = self.post()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["jobs"], [])
        self.assertEqual(data["status"], "unavailable")
        self.assertIn("Himalayas could not be reached", " ".join(data["notes"]))
        self.assertNotIn("PROVIDER-SECRET-BODY", response.text)
        self.himalayas = {"totalCount": 1, "jobs": [posting("Data Analyst")]}
        self.assertEqual(len(self.post().json()["jobs"]), 1)

    def test_malformed_provider_payload_is_handled(self):
        self.himalayas = {"jobs": "nope"}
        data = self.post().json()
        self.assertEqual(data["jobs"], [])

    def web_tools(self):
        grounded = "https://www.brightermonday.co.ke/listings/data-analyst-x86pnj"
        return [
            {"name": "browser.search", "type": "browser_search", "arguments": "{\"query\": \"Data Analyst Kenya\"}",
             "output": "L0: \nL1: URL:\nL2: https://exa.ai/search?q=Data+Analyst+Kenya",
             "search_results": {"results": [{"title": "Data Analyst at Kenya Airways | BrighterMonday", "url": grounded, "content": "", "score": 0},
                                            {"title": "Jane Doe", "url": "https://www.linkedin.com/in/jane-doe", "content": "", "score": 0}]}},
            {"name": "browser.open", "type": "browser.open", "arguments": "{\"cursor\": 0, \"id\": 1}",
             "output": "L0: \nL1: URL: https://www.fuzu.com/kenya/jobs/data-analyst-syngenta-kenya\nL2: Data Analyst at Syngenta Kenya \\| Fuzu\nL3: \nL4: 3 days ago\nL5: Experience with SQL, Excel and Smartsheet.",
             "search_results": {"results": []}},
            {"name": "browser.open", "type": "browser.open", "arguments": "{}",
             "output": "L0: \nL1: URL: https://www.fuzu.com/jobs/data-analyst\nL2: Research Jobs in Kenya — Latest Vacancies \\| Fuzu", "search_results": {"results": []}},
        ]

    def test_web_results_require_grounding(self):
        content = json.dumps({"jobs": [
            {"title": "Data Analyst", "company": "Kenya Airways", "location": "Nairobi", "url": "https://www.brightermonday.co.ke/listings/data-analyst-x86pnj",
             "posted": "2026-09-27", "source": "BrighterMonday", "requirements": ["Excel, SQL and Power BI", "Python an added plus"]},
            {"title": "Data Analyst", "company": "Invented Ltd", "url": "https://invented.example/jobs/data-analyst", "posted": "2026-09-26"},
            {"title": "Data Analyst", "company": "Profile", "url": "https://www.linkedin.com/in/jane-doe"},
        ]})
        self.groq = groq_envelope(f"Here you go:\n```json\n{content}\n```", self.web_tools())
        response = self.post(source="web")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        urls = [job["url"] for job in data["jobs"]]
        self.assertIn("https://www.brightermonday.co.ke/listings/data-analyst-x86pnj", urls)
        self.assertIn("https://www.fuzu.com/kenya/jobs/data-analyst-syngenta-kenya", urls)
        self.assertNotIn("https://invented.example/jobs/data-analyst", urls)
        self.assertFalse(any("linkedin.com/in/" in url or url.endswith("/jobs/data-analyst") for url in urls))
        self.assertTrue(all(job["kind"] == "local" for job in data["jobs"]))
        airways = next(job for job in data["jobs"] if job["company"] == "Kenya Airways")
        self.assertEqual(airways["posted"], "2026-09-27")
        self.assertEqual(airways["matched_skills"], ["excel", "sql"])
        self.assertIn("python", airways["missing_skills"])
        syngenta = next(job for job in data["jobs"] if job["company"] == "Syngenta Kenya")
        self.assertEqual(syngenta["source"], "Fuzu")
        self.assertIsNotNone(syngenta["posted"])
        self.assertIn("1 search result(s) were hidden", " ".join(data["notes"]))
        request = json.loads(self.calls[0].content)
        self.assertEqual(request["tools"], [{"type": "browser_search"}])
        prompt = json.dumps(request["messages"])
        self.assertIn("Data Analyst", prompt)
        self.assertIn("Kenya", prompt)
        self.assertNotIn("jobs-test-secret", response.text)

    def test_web_drops_everything_when_ungrounded(self):
        content = json.dumps({"jobs": [{"title": "Data Analyst", "company": "X", "url": "https://jobs.example/1"}]})
        self.groq = groq_envelope(content, [{"name": "browser.search", "output": "no links here", "search_results": {"results": []}}])
        data = self.post(source="web").json()
        self.assertEqual(data["jobs"], [])

    def test_web_drops_stale_postings_and_future_dates(self):
        old, future = "https://www.myjobmag.co.ke/job/data-analyst-old", "https://www.myjobmag.co.ke/job/data-analyst-new"
        content = json.dumps({"jobs": [{"title": "Data Analyst", "company": "Old Co", "url": old, "posted": "2024-01-10"},
                                       {"title": "Data Analyst", "company": "New Co", "url": future + ").", "posted": "2099-01-01"}]})
        tools = [{"name": "browser.search", "search_results": {"results": [{"title": "a", "url": old}, {"title": "b", "url": future}]}}]
        self.groq = groq_envelope(content, tools)
        data = self.post(source="web").json()
        self.assertEqual([(job["company"], job["url"], job["posted"]) for job in data["jobs"]], [("New Co", future, None)])

    def test_web_failure_and_unconfigured(self):
        self.groq = None
        response = self.post(source="web")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["jobs"], [])
        self.assertIn("Web search could not be reached", " ".join(response.json()["notes"]))
        self.assertNotIn("PROVIDER-SECRET-BODY", response.text)
        self.calls.clear()
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            data = self.post(source="web").json()
        self.assertEqual(data["jobs"], [])
        self.assertEqual(data["status"], "not_configured")
        self.assertIn("not configured", " ".join(data["notes"]))
        self.assertEqual(self.calls, [])

    def test_salary_and_title_helpers(self):
        self.assertEqual(jobs.salary({"minSalary": 70000, "maxSalary": 95000, "currency": "USD", "salaryPeriod": "annual"}), "USD 70,000–95,000 / year")
        self.assertEqual(jobs.salary({"minSalary": 2500, "maxSalary": 2500, "currency": "EUR", "salaryPeriod": "monthly"}), "EUR 2,500 / month")
        self.assertIsNone(jobs.salary({"minSalary": None, "maxSalary": None, "currency": "USD"}))
        self.assertEqual(jobs._split_title("Data Analyst at Kenya Airways September, 2026 \\| MyJobMag"), ("Data Analyst", "Kenya Airways", "MyJobMag"))


if __name__ == "__main__":
    unittest.main()
