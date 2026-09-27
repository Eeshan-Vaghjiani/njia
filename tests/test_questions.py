import json
import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
import httpx

from njia import advisor, questions
from njia.app import app

CV = ("Name: Synthetic Candidate\nEmail: person@example.com\n+254 712 345 678\n"
      "Built a Power BI dashboard comparing sales by branch.\n"
      "Used SQL to join two sales tables.\nPrepared a monthly sales summary for the operations team.")
REAL_CLIENT = httpx.AsyncClient


def envelope(content, model="openai/gpt-oss-20b"):
    return {"model": model, "choices": [{"finish_reason": "stop", "message": {"content": content}}]}


def mock_client(handler, module="njia.groq_client"):
    return patch(f"{module}.httpx.AsyncClient", side_effect=lambda **kwargs: REAL_CLIENT(
        transport=httpx.MockTransport(handler), **kwargs))


class QuestionsEndpointTests(unittest.TestCase):
    def setUp(self):
        environment = patch.dict(os.environ, {"GROQ_API_KEY": "questions-test-secret", "GROQ_MODEL": "", "NJIA_ADVISOR_MODEL": ""})
        environment.start()
        self.addCleanup(environment.stop)
        self.client = TestClient(app)
        self.payload = {"text": CV, "country": "Kenya", "role": "Data Analyst", "consent": True}
        self.generated = {"questions": [
            {"type": "skill", "skill": "Python", "question": "Have you used Python for data analysis?", "why": "Python is common in Data Analyst roles but not shown in your CV."},
            {"type": "skill", "skill": "python", "question": "Duplicate Python question?", "why": "Duplicate."},
            {"type": "skill", "skill": "imaginary-skill", "question": "Have you used it?", "why": "Unknown skill."},
            {"type": "skill", "skill": "power bi", "question": "Did your Power BI dashboard use DAX measures?", "why": "DAX shows deeper Power BI skill."},
            {"type": "skill", "skill": "r", "question": "Have you used R?", "why": "Visit https://example.com for more."},
            {"type": "skill", "skill": "excel", "question": "Have you used Excel?", "why": "Excel is in 48% of postings."},
            {"type": "skill", "skill": "tableau", "question": "Have you built charts in Tableau?", "why": "Tableau is another common BI tool."},
            {"type": "skill", "skill": "spss", "question": "Have you used SPSS?", "why": "Some employers ask for it."},
            {"type": "detail", "skill": "power bi", "quote": "Built a Power BI dashboard", "question": "Who used the dashboard from “Built a Power BI dashboard”, and how often?", "why": "Naming the audience makes the line stronger."},
            {"type": "detail", "skill": None, "quote": "Led a team of 40 analysts", "question": "How big was the team?", "why": "Only answer if true."},
        ]}
        self.calls = []

    def handler(self, content=None):
        def handle(request):
            self.calls.append(request)
            return httpx.Response(200, json=envelope(json.dumps(self.generated) if content is None else content))
        return handle

    def post(self, handler, payload=None):
        with mock_client(handler):
            return self.client.post("/api/questions", json=payload or self.payload)

    def test_consent_and_market_are_required_without_provider_call(self):
        with patch("njia.groq_client.httpx.AsyncClient") as client:
            response = self.client.post("/api/questions", json={**self.payload, "consent": False})
            self.assertEqual(response.status_code, 422)
            self.assertIn("Consent is required", response.json()["detail"])
            for values in ({"role": "Astronaut"}, {"country": "Atlantis"}, {"text": " " * 20}, {"text": "x" * 15001}):
                with self.subTest(values=values):
                    self.assertEqual(self.client.post("/api/questions", json={**self.payload, **values}).status_code, 422)
            client.assert_not_called()

    def test_groq_questions_are_validated_capped_and_canonical(self):
        response = self.post(self.handler())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(set(data), {"mode", "model", "questions", "note"})
        self.assertEqual(data["mode"], "groq")
        self.assertEqual(data["model"], "openai/gpt-oss-20b")
        items = data["questions"]
        self.assertTrue(3 <= len(items) <= 5)
        self.assertEqual([item["id"] for item in items], [f"q{i}" for i in range(1, len(items) + 1)])
        for item in items:
            self.assertEqual(set(item), {"id", "type", "skill", "question", "why", "options"})
            self.assertLessEqual(len(item["question"]), 300)
            self.assertLessEqual(len(item["why"]), 300)
        skill_items = [item for item in items if item["type"] == "skill"]
        self.assertEqual([item["skill"] for item in skill_items], ["python", "power bi", "tableau", "spss"])
        self.assertTrue(all(item["options"] == list(advisor.SKILL_OPTIONS) for item in skill_items))
        detail = [item for item in items if item["type"] == "detail"]
        self.assertEqual(len(detail), 1)
        self.assertEqual(detail[0]["options"], [])
        self.assertIn("Built a Power BI dashboard", detail[0]["question"])
        self.assertIn("Only answer if true", detail[0]["why"])
        self.assertNotIn("example.com", response.text)
        self.assertNotIn("40 analysts", response.text)
        self.assertNotIn("48%", response.text)
        # One request, JSON mode, scrubbed CV, instructions separated from untrusted data.
        self.assertEqual(len(self.calls), 1)
        payload = json.loads(self.calls[0].content)
        self.assertEqual(payload["response_format"], {"type": "json_object"})
        self.assertEqual(payload["messages"][0]["content"], questions.SYSTEM_PROMPT)
        self.assertIn("UNTRUSTED DATA", payload["messages"][0]["content"])
        context = json.loads(payload["messages"][1]["content"])
        self.assertIn("python", context["not_evidenced_top_skills"])
        self.assertTrue(set(context["market_context"]["top_skill_ids"]) <= set(context["allowed_skill_ids"]))
        for private in ("Synthetic Candidate", "person@example.com", "254 712"):
            self.assertNotIn(private, self.calls[0].content.decode())

    def test_invalid_model_output_falls_back_to_curated(self):
        too_few = {"questions": [self.generated["questions"][0], self.generated["questions"][2]]}
        for content in ("not json", "[]", json.dumps({"questions": "none"}), json.dumps({**self.generated, "extra": 1}),
                        json.dumps(too_few), json.dumps({"questions": [{"type": "open", "question": "Q", "why": "W"}] * 3})):
            with self.subTest(content=content[:40]):
                data = self.post(self.handler(content)).json()
                self.assertEqual(data["mode"], "curated")
                self.assertIsNone(data["model"])
        for status in (401, 500):
            with self.subTest(status=status):
                data = self.post(lambda request: httpx.Response(status, text="questions-test-secret PRIVATE")).json()
                self.assertEqual(data["mode"], "curated")
                self.assertNotIn("PRIVATE", json.dumps(data))

    def test_missing_key_returns_curated_without_network(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": " "}), patch("njia.groq_client.httpx.AsyncClient") as client:
            data = self.client.post("/api/questions", json=self.payload).json()
            client.assert_not_called()
        self.assertEqual(data["mode"], "curated")
        self.assertIsNone(data["model"])
        self.assertIn("key missing", data["note"])
        items = data["questions"]
        self.assertTrue(3 <= len(items) <= 5)
        skills = [item["skill"] for item in items if item["type"] == "skill"]
        self.assertEqual(skills, ["excel", "python", "r"])
        self.assertIn("Have you used Python? It appears in", items[1]["question"])
        self.assertIn("historical Data Analyst postings in the Kenya sample", items[1]["question"])
        self.assertEqual(items[-1]["type"], "detail")
        self.assertEqual(items[-1]["options"], [])
        self.assertTrue(all(item["options"] == list(advisor.SKILL_OPTIONS) for item in items if item["type"] == "skill"))


class AnswersAdvisorTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        environment = patch.dict(os.environ, {"GROQ_API_KEY": "advisor-test-secret", "GROQ_MODEL": "", "NJIA_ADVISOR_MODEL": ""})
        environment.start()
        self.addCleanup(environment.stop)
        self.generated = {
            "summary": "Your reporting experience is a starting point for a Data Analyst role.",
            "strengths": [{"skill": "sql", "evidence": "Used SQL to join two sales tables."}],
            "gaps": [{"skill": "python", "reason": "Python is not evidenced in this CV.", "first_step": "Load a synthetic CSV."}],
            "cv_improvements": [{"before": "Built a Power BI dashboard comparing sales by branch.",
                                 "after": "Built a Power BI dashboard comparing sales across 3 branches, used weekly by 12 managers.",
                                 "reason": "Uses your answer — verify. Names the audience and scale."}],
            "seven_day_plan": [{"day": i, "action": f"Practice step {i}.", "deliverable": "A saved output."} for i in range(1, 8)],
            "interview": {"question": "How do you check a JOIN?", "what_good_looks_like": "Row counts and key checks."},
            "suggested_skills": ["sql", "power bi", "tableau"], "limitations": [],
        }
        self.answers = [
            {"id": "q1", "type": "skill", "skill": "Python", "question": "Have you used Python?", "answer": "Used it in a project or course"},
            {"id": "q2", "type": "skill", "skill": "tableau", "question": "Have you used Tableau?", "answer": "Not yet"},
            {"id": "q3", "type": "skill", "skill": "r", "question": "Have you used R?", "answer": "Still learning it"},
            {"id": "q4", "type": "detail", "skill": None, "question": "Who used the dashboard?", "answer": "12 managers used it weekly across 3 branches. Email me at person@example.com"},
        ]
        self.requests = []

    async def assess(self, answers):
        def handler(request):
            self.requests.append(json.loads(request.content))
            return httpx.Response(200, json=envelope(json.dumps(self.generated)))
        with mock_client(handler, "njia.advisor"):
            return await advisor.assess_cv(CV, "Kenya", "Data Analyst", answers=answers)

    async def test_answers_shape_skills_prompt_and_allow_answer_facts(self):
        result = await self.assess(self.answers)
        self.assertEqual(result["mode"], "groq")
        self.assertEqual(result["suggested_skills"], ["sql", "power bi", "python"])
        self.assertEqual(result["answers_used"], {"added": ["python"], "removed": ["tableau"], "details": 1})
        self.assertEqual(len(result["cv_improvements"]), 1)
        self.assertTrue(result["cv_improvements"][0]["reason"].startswith("Uses your answer — verify. Names"))
        self.assertTrue(result["gaps"][0]["reason"].startswith("You said you have used it in a project or course"))
        payload = self.requests[0]
        self.assertEqual(payload["max_completion_tokens"], 3500)
        self.assertEqual(payload["response_format"], {"type": "json_object"})
        self.assertEqual(payload["messages"][0]["content"], advisor.SYSTEM_PROMPT + advisor.ANSWERS_PROMPT)
        context = json.loads(payload["messages"][1]["content"])
        self.assertEqual([item["skill"] for item in context["candidate_answers"]], ["python", "tableau", "r", None])
        self.assertNotIn("person@example.com", json.dumps(payload))

    async def test_answer_numbers_are_rejected_without_detail_answers(self):
        skill_only = [answer for answer in self.answers if answer["type"] == "skill"]
        for answers in (None, skill_only):
            with self.subTest(answers=bool(answers)):
                result = await self.assess(answers)
                self.assertEqual(result["mode"], "groq")
                self.assertEqual(result["cv_improvements"], [])
                self.assertIn("Rejected 1 CV rewrites", " ".join(result["limitations"]))
        # A skill-option answer never authorizes a new tool in a rewrite.
        self.generated["cv_improvements"][0]["after"] = "Built a Power BI and Python dashboard comparing sales by branch."
        result = await self.assess(skill_only)
        self.assertEqual(result["cv_improvements"], [])

    async def test_no_answers_keep_existing_result_keys(self):
        for answers in (None, [], [{"id": "q1", "type": "skill", "skill": "python", "question": "Q", "answer": "Maybe"}]):
            with self.subTest(answers=answers):
                result = await self.assess(answers)
                self.assertEqual(set(result), {"mode", "model", *self.generated})
                self.assertEqual(self.requests[-1]["messages"][0]["content"], advisor.SYSTEM_PROMPT)

    async def test_curated_fallback_applies_answers(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            result = await advisor.assess_cv(CV, "Kenya", "Data Analyst", answers=self.answers)
        self.assertEqual(result["mode"], "curated")
        self.assertIn("python", result["suggested_skills"])
        self.assertNotIn("python", [gap["skill"] for gap in result["gaps"]])
        self.assertEqual(result["answers_used"], {"added": ["python"], "removed": ["tableau"], "details": 0})
        self.assertIn("Detail answers are used only by the AI brief", " ".join(result["limitations"]))


class AdviseEndpointAnswersTests(unittest.TestCase):
    def test_advise_accepts_answers_and_validates_them(self):
        generated = {
            "summary": "A starting point.", "strengths": [], "gaps": [], "cv_improvements": [],
            "seven_day_plan": [{"day": i, "action": "Practice.", "deliverable": "Output."} for i in range(1, 8)],
            "interview": {"question": "Q?", "what_good_looks_like": "A clear answer."},
            "suggested_skills": ["sql"], "limitations": [],
        }
        sent = []

        def handler(request):
            sent.append(json.loads(request.content))
            return httpx.Response(200, json=envelope(json.dumps(generated)))

        client = TestClient(app)
        payload = {"text": CV, "country": "Kenya", "role": "Data Analyst", "consent": True, "answers": [
            {"id": "q1", "type": "skill", "skill": "python", "question": "Have you used Python?", "answer": "Used it at work"}]}
        with patch.dict(os.environ, {"GROQ_API_KEY": "advisor-test-secret"}), mock_client(handler, "njia.advisor"):
            response = client.post("/api/advise", json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["advisor"]["answers_used"], {"added": ["python"], "removed": [], "details": 0})
            self.assertIn("python", data["market"]["confirmed_skills"])
            self.assertIn("candidate_answers", json.loads(sent[0]["messages"][1]["content"]))
            for invalid in ({"type": "other"}, {"answer": "x" * 401}, {"question": "q" * 301}):
                with self.subTest(invalid=invalid):
                    bad = {**payload, "answers": [{**payload["answers"][0], **invalid}]}
                    self.assertEqual(client.post("/api/advise", json=bad).status_code, 422)
            self.assertEqual(client.post("/api/advise", json={**payload, "answers": payload["answers"] * 7}).status_code, 422)
            self.assertEqual(len(sent), 1)


if __name__ == "__main__":
    unittest.main()
