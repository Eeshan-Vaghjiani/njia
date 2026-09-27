"""Groq-first, NVIDIA-API-Catalog-second failover for JSON calls; never for web search."""
import json
import os
import unittest
from unittest.mock import patch

import httpx

from njia import advisor, groq_client, interview, questions

CV = ("Operations assistant. Built Excel pivot tables for weekly reports.\n"
      "Used SQL to join two sales tables.\nPrepared a monthly sales summary.")
BRIEF = {
    "summary": "Reporting experience is a starting point for a Data Analyst role.",
    "strengths": [{"skill": "excel", "evidence": "Built Excel pivot tables for weekly reports."}],
    "gaps": [{"skill": "python", "reason": "Python is not evidenced in this CV.", "first_step": "Load a synthetic CSV."}],
    "cv_improvements": [],
    "seven_day_plan": [{"day": i, "action": f"Practice step {i}.", "deliverable": "A saved exercise."} for i in range(1, 8)],
    "interview": {"question": "How do you check a JOIN?", "what_good_looks_like": "Row counts and unmatched keys."},
    "suggested_skills": ["excel", "sql"], "limitations": [],
}


def envelope(content, model="openai/gpt-oss-20b"):
    return httpx.Response(200, json={"model": model, "choices": [
        {"finish_reason": "stop", "message": {"role": "assistant", "content": content}}]})


class FailoverTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {"GROQ_API_KEY": "groq-test-secret", "NVIDIA_API_KEY": "nvapi-test-secret",
                                                   "GROQ_MODEL": "", "NJIA_ADVISOR_MODEL": "", "NJIA_FALLBACK_MODEL": ""})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.client_class = httpx.AsyncClient
        self.requests = []

    def mock(self, module, groq, nvidia):
        def handler(request):
            payload = json.loads(request.content)
            self.requests.append((request.url.host, request.headers["Authorization"], payload))
            return groq(payload) if request.url.host == "api.groq.com" else nvidia(payload)

        return patch(f"njia.{module}.httpx.AsyncClient", side_effect=lambda **options: self.client_class(
            transport=httpx.MockTransport(handler), **options))

    @staticmethod
    def limited(_payload):
        return httpx.Response(429, json={"error": {"message": "Rate limit reached"}})

    async def test_chat_falls_back_to_same_model_on_nvidia(self):
        with self.mock("groq_client", self.limited, lambda p: envelope('{"ok": true}')):
            content, message, model = await groq_client.chat([{"role": "user", "content": "hi"}])
        self.assertEqual((content, model, groq_client.provider(message)), ('{"ok": true}', "openai/gpt-oss-20b", "nvidia"))
        (groq_host, _, _), (nvidia_host, auth, payload) = self.requests
        self.assertEqual((groq_host, nvidia_host), ("api.groq.com", "integrate.api.nvidia.com"))
        self.assertEqual(auth, "Bearer nvapi-test-secret")
        self.assertEqual(payload["model"], "openai/gpt-oss-20b")
        self.assertEqual(payload["max_tokens"], 2000)
        self.assertNotIn("max_completion_tokens", payload)
        self.assertEqual(payload["response_format"], {"type": "json_object"})

    async def test_groq_success_never_calls_nvidia(self):
        with self.mock("groq_client", lambda p: envelope('{"ok": 1}'), self.limited):
            _, message, _ = await groq_client.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(groq_client.provider(message), "groq")
        self.assertEqual([host for host, _, _ in self.requests], ["api.groq.com"])

    async def test_web_search_never_falls_back(self):
        with self.mock("groq_client", self.limited, lambda p: envelope("text")):
            with self.assertRaises(groq_client.ProviderError):
                await groq_client.chat([{"role": "user", "content": "hi"}], tools=groq_client.BROWSER_SEARCH)
        self.assertEqual([host for host, _, _ in self.requests], ["api.groq.com"])

    async def test_nvidia_alone_serves_json_calls_without_groq_key(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}), self.mock("groq_client", self.limited, lambda p: envelope('{"a": 1}')):
            _, message, _ = await groq_client.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(groq_client.provider(message), "nvidia")
        self.assertEqual([host for host, _, _ in self.requests], ["integrate.api.nvidia.com"])

    async def test_both_failing_raises_generic_error(self):
        with self.mock("groq_client", self.limited, self.limited):
            with self.assertRaises(groq_client.ProviderError) as caught:
                await groq_client.chat([{"role": "user", "content": "hi"}])
        self.assertNotIn("secret", str(caught.exception))

    async def test_brief_falls_back_and_labels_nvidia(self):
        with self.mock("advisor", self.limited, lambda p: envelope(json.dumps(BRIEF))):
            result = await advisor.assess_cv(CV, "Kenya", "Data Analyst")
        self.assertEqual((result["mode"], result["model"]), ("nvidia", "openai/gpt-oss-20b"))
        self.assertEqual(result["strengths"], BRIEF["strengths"])
        self.assertEqual(self.requests[1][2]["max_tokens"], 3500)
        self.assertNotIn("nvapi-test-secret", json.dumps(result))

    async def test_brief_curated_when_both_fail(self):
        with self.mock("advisor", self.limited, self.limited):
            result = await advisor.assess_cv(CV, "Kenya", "Data Analyst")
        self.assertEqual(result["mode"], "curated")
        self.assertIn("NVIDIA fallback", " ".join(result["limitations"]))

    async def test_invalid_nvidia_brief_is_still_rejected(self):
        bad = {**BRIEF, "strengths": [{"skill": "excel", "evidence": "Invented quote not in the CV."}]}
        with self.mock("advisor", self.limited, lambda p: envelope(json.dumps({**bad, "seven_day_plan": bad["seven_day_plan"][:3]}))):
            result = await advisor.assess_cv(CV, "Kenya", "Data Analyst")
        self.assertEqual(result["mode"], "curated")

    async def test_questions_and_feedback_report_nvidia_mode(self):
        generated = {"questions": [
            {"type": "skill", "skill": "python", "question": "Have you used Python for analysis?", "why": "Only answer if true."},
            {"type": "skill", "skill": "tableau", "question": "Have you built Tableau charts?", "why": "Only answer if true."}]}
        with self.mock("groq_client", self.limited, lambda p: envelope(json.dumps(generated))):
            result = await questions.generate(CV, "Kenya", "Data Analyst")
        self.assertEqual(result["mode"], "nvidia")
        feedback = {"score": 3, "verdict": "A clear start.", "star": {"situation": True, "task": True, "action": True, "result": False},
                    "strengths": ["Specific actions."], "improvements": ["State the result."],
                    "stronger_answer": "Situation: weekly totals did not match. Action: I checked the spreadsheets. Result: [your result]."}
        body = interview.FeedbackRequest(role="Data Analyst", question="Tell me about a data problem.", consent=True,
                                         answer="Weekly totals did not match, so I checked the spreadsheets and flagged duplicates.")
        with self.mock("groq_client", self.limited, lambda p: envelope(json.dumps(feedback))):
            result = await interview.interview_feedback(body)
        self.assertEqual((result["mode"], result["score"]), ("nvidia", 3))


if __name__ == "__main__":
    unittest.main()
