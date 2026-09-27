import json
import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
import httpx

from njia import engine, groq_client, interview
from njia.app import app

MODEL = "openai/gpt-oss-20b"
SECRET = "interview-test-secret"


def search_envelope(questions, results, content=None):
    message = {
        "role": "assistant",
        "content": json.dumps({"questions": questions}) if content is None else content,
        "executed_tools": [
            {"name": "browser.search", "index": 0, "type": "browser_search", "arguments": "{\"query\": \"q\"}",
             "output": "L0: \nL1: URL:\nL2: https://exa.ai/search?q=data+analyst\nL3: # Search Results\n"
                       "L5: \\* 【0†Guide†kenyatrends.co.ke】\nL8: https://only-in-page-text.example/post/1",
             "search_results": {"results": [{"title": title, "url": url, "content": "", "score": "0"}
                                            for title, url in results]}},
        ],
    }
    return {"model": MODEL, "choices": [{"finish_reason": "stop", "message": message}]}


def question(text, url, category="technical", skill="sql"):
    return {"question": text, "category": category, "skill": skill, "source_title": "Model title",
            "source_url": url, "why_asked": "Tests core skills.", "how_to_prepare": "Practise on sample data."}


RESULTS = [
    ("Interview guide for Data Analyst Role - Trends", "https://kenyatrends.co.ke/interview-guide-for-data-analyst-role/"),
    ("Data Analyst Interview Questions", "https://www.coursera.org/articles/data-analyst-interview-questions"),
    ("r/datascience interview thread", "https://www.reddit.com/r/datascience/comments/abc/interview/"),
]


class InterviewTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {"NVIDIA_API_KEY": "", "GROQ_API_KEY": SECRET, "GROQ_MODEL": "", "NJIA_ADVISOR_MODEL": ""})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        interview._cache.clear()
        self.addCleanup(interview._cache.clear)
        self.client = TestClient(app)
        self.client_class = httpx.AsyncClient
        self.calls = []

    def mocked(self, respond):
        def handler(request):
            self.calls.append(json.loads(request.content))
            self.assertEqual(request.headers["Authorization"], f"Bearer {SECRET}")
            return respond(request)
        return patch("njia.groq_client.httpx.AsyncClient", side_effect=lambda **kwargs: self.client_class(
            transport=httpx.MockTransport(handler), **kwargs))

    def questions(self, envelope, **body):
        with self.mocked(lambda request: httpx.Response(200, json=envelope)):
            response = self.client.post("/api/interview/questions", json={"country": "Kenya", "role": "Data Analyst", **body})
        self.assertEqual(response.status_code, 200)
        return response.json()

    def assert_curated(self, data, role="Data Analyst"):
        self.assertEqual(data["mode"], "curated")
        self.assertIsNone(data["model"])
        self.assertEqual(data["note"], interview.CURATED_NOTE)
        self.assertEqual(data["sources"], [])
        self.assertGreaterEqual(len(data["questions"]), 6)
        self.assertTrue(all(q["source_url"] is None for q in data["questions"]))
        self.assertEqual(data["questions"][0]["question"], interview.CURATED[interview.ROLE_FAMILY[role]][0][0])

    def test_grounded_questions_kept_and_ungrounded_dropped(self):
        items = [
            question("What are pivot tables and how do you use them? Email me at a@b.co", RESULTS[0][1], "tool", "Excel"),
            question("What types of SQL joins are there?", "http://kenyatrends.co.ke/interview-guide-for-data-analyst-role", "technical", "SQL"),
            question("Tell me about a time you missed a deadline.", RESULTS[1][1], "behavioral", None),
            question("How would you investigate falling sales?", "https://reddit.com/r/datascience/comments/abc/interview", "case", "not-a-skill"),
            question("Invented source question?", "https://invented.example/questions"),
            question("Linked only inside page text?", "https://only-in-page-text.example/post/1"),
            question("Search page as a source?", "https://exa.ai/search?q=data+analyst"),
            question("What types of SQL joins are there?", RESULTS[1][1]),
            question("Bad category question?", RESULTS[2][1], "trivia"),
            {**question("Extra field question?", RESULTS[2][1]), "salary": "x"},
        ]
        data = self.questions(search_envelope(items, RESULTS), skills=["excel"])
        self.assertEqual(data["mode"], "web")
        self.assertEqual(data["model"], MODEL)
        self.assertEqual(len(self.calls), 1)
        payload = self.calls[0]
        self.assertEqual(payload["tools"], groq_client.BROWSER_SEARCH)
        self.assertNotIn("response_format", payload)
        self.assertEqual(set(json.loads(payload["messages"][1]["content"])), {"role", "country", "focus_skill_ids", "focus_skills"})
        texts = [q["question"] for q in data["questions"]]
        self.assertEqual(len(texts), 4)
        self.assertNotIn("Invented source question?", texts)
        self.assertNotIn("Linked only inside page text?", texts)
        self.assertNotIn("Search page as a source?", texts)
        self.assertIn("[email removed]", texts[0])
        first = data["questions"][0]
        self.assertEqual((first["skill"], first["category"]), ("excel", "tool"))
        self.assertEqual(first["source_title"], RESULTS[0][0])
        by_text = {q["question"]: q for q in data["questions"]}
        self.assertEqual(by_text["Tell me about a time you missed a deadline."]["category"], "behavioural")
        self.assertIsNone(by_text["How would you investigate falling sales?"]["skill"])
        self.assertEqual(by_text["What types of SQL joins are there?"]["skill"], "sql")
        self.assertEqual(len(data["sources"]), 4)
        self.assertTrue(all(set(s) == {"title", "url"} for s in data["sources"]))
        self.assertTrue(data["fetched_at"])
        self.assertNotIn(SECRET, json.dumps(data))

    def test_fewer_than_three_grounded_questions_use_curated_bank(self):
        items = [question("What are pivot tables?", RESULTS[0][1]), question("What is a JOIN?", RESULTS[1][1]),
                 question("Invented?", "https://invented.example/a"), question("Invented too?", "https://invented.example/b")]
        self.assert_curated(self.questions(search_envelope(items, RESULTS)))

    def test_no_executed_tools_means_no_grounding(self):
        items = [question(f"Grounded question number {i}?", RESULTS[i % 3][1]) for i in range(6)]
        envelope = search_envelope(items, RESULTS)
        del envelope["choices"][0]["message"]["executed_tools"]
        self.assert_curated(self.questions(envelope))
        # Without structured results, URLs printed in the tool output are the evidence.
        message = {"executed_tools": [{"output": "L1: URL: https://kenyatrends.co.ke/guide/\n【0†Guide†kenyatrends.co.ke】"}]}
        self.assertEqual(set(interview._evidence(message)), {"https://kenyatrends.co.ke/guide"})

    def test_invalid_json_and_provider_errors_use_curated_bank(self):
        self.assert_curated(self.questions(search_envelope([], RESULTS, content="Sorry, I could not search.")))
        interview._cache.clear()
        self.assert_curated(self.questions(search_envelope([], RESULTS, content='{"questions": [1, 2], "questions": []}')))
        interview._cache.clear()
        with self.mocked(lambda request: httpx.Response(500, json={"error": SECRET})):
            data = self.client.post("/api/interview/questions", json={"country": "Kenya", "role": "Cloud Engineer"}).json()
        self.assert_curated(data, "Cloud Engineer")
        self.assertNotIn(SECRET, json.dumps(data))

    def test_missing_key_uses_curated_bank_without_http(self):
        with patch.dict(os.environ, {"NVIDIA_API_KEY": "", "GROQ_API_KEY": ""}), patch("njia.groq_client.httpx.AsyncClient") as client:
            data = self.client.post("/api/interview/questions", json={"country": "Kenya", "role": "Data Engineer"}).json()
            client.assert_not_called()
        self.assert_curated(data, "Data Engineer")

    def test_results_are_cached_per_country_and_role(self):
        items = [question(f"Grounded question number {i}?", RESULTS[i % 3][1]) for i in range(6)]
        first = self.questions(search_envelope(items, RESULTS))
        second = self.questions(search_envelope([], RESULTS))
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(first["questions"], second["questions"])
        self.assertEqual(second["mode"], "web")
        self.questions(search_envelope(items, RESULTS), country="Nigeria")
        self.assertEqual(len(self.calls), 2)

    def test_question_request_validation(self):
        for body in ({"country": "Atlantis", "role": "Data Analyst"}, {"country": "Kenya", "role": "Astronaut"},
                     {"country": "Kenya", "role": "Data Analyst", "skills": ["not-a-skill"]},
                     {"country": "Kenya", "role": "Data Analyst", "skills": ["sql"] * 101}):
            with self.subTest(body=body):
                self.assertEqual(self.client.post("/api/interview/questions", json=body).status_code, 422)

    def test_curated_bank_covers_every_role_with_valid_entries(self):
        vocabulary = set(engine.vocabulary())
        self.assertEqual(set(interview.ROLE_FAMILY), set(engine.metadata()["roles"]))
        for items in interview.CURATED.values():
            self.assertGreaterEqual(len(items), 6)
            for text, category, skill, why, how in items:
                self.assertIn(category, interview.CATEGORIES)
                self.assertTrue(skill is None or skill in vocabulary)
                self.assertTrue(len(text) <= 400 and len(why) <= 300 and len(how) <= 300)


ANSWER = ("When I worked at a Nairobi retail cooperative I had to check weekly stock records. "
          "I built an Excel pivot table across 3 branches and flagged duplicate entries. Contact me: jane@example.com or +254 712 345 678.")
FEEDBACK = {
    "score": 4, "verdict": "Clear and specific; the result needs to be stated.",
    "star": {"situation": True, "task": True, "action": True, "result": False},
    "strengths": ["You explain the situation and your own actions clearly."],
    "improvements": ["State the outcome of flagging duplicates."],
    "stronger_answer": "Situation: At a Nairobi retail cooperative.\nTask: Check weekly stock records.\n"
                       "Action: I built an Excel pivot table across 3 branches and flagged duplicates.\nResult: [your result]",
}


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {"NVIDIA_API_KEY": "", "GROQ_API_KEY": SECRET, "GROQ_MODEL": "", "NJIA_ADVISOR_MODEL": ""})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.client = TestClient(app)
        self.client_class = httpx.AsyncClient
        self.calls = []
        self.body = {"role": "Data Analyst", "question": "Tell me about a time you found an error in data.",
                     "answer": ANSWER, "consent": True}

    def feedback(self, generated, **body):
        def handler(request):
            self.calls.append(json.loads(request.content))
            content = generated if isinstance(generated, str) else json.dumps(generated)
            return httpx.Response(200, json={"model": MODEL, "choices": [{"finish_reason": "stop", "message": {"content": content}}]})
        with patch("njia.groq_client.httpx.AsyncClient", side_effect=lambda **kwargs: self.client_class(
                transport=httpx.MockTransport(handler), **kwargs)):
            response = self.client.post("/api/interview/feedback", json={**self.body, **body})
        self.assertEqual(response.status_code, 200)
        return response.json()

    def assert_checklist(self, data):
        self.assertEqual(data["mode"], "checklist")
        self.assertIsNone(data["model"])
        self.assertEqual(data["note"], interview.CHECKLIST_NOTE)
        self.assertIn(data["score"], range(1, 6))
        self.assertEqual(set(data["star"]), {"situation", "task", "action", "result"})
        self.assertIn("[your result", data["stronger_answer"])
        self.assertLessEqual(len(data["strengths"]), 3)
        self.assertLessEqual(len(data["improvements"]), 3)

    def test_consent_and_input_validation(self):
        with patch("njia.groq_client.httpx.AsyncClient") as client:
            response = self.client.post("/api/interview/feedback", json={**self.body, "consent": False})
            self.assertEqual(response.status_code, 422)
            self.assertIn("consent", response.json()["detail"])
            for extra in ({"answer": "too short"}, {"answer": "x" * 3001}, {"question": "q" * 501},
                          {"role": "Astronaut"}, {"evidence": "e" * 701}):
                with self.subTest(extra=list(extra)):
                    self.assertEqual(self.client.post("/api/interview/feedback", json={**self.body, **extra}).status_code, 422)
            client.assert_not_called()

    def test_valid_ai_feedback_and_pii_scrubbed_in_request(self):
        data = self.feedback(FEEDBACK, evidence="Used Excel pivot tables to summarise weekly sales across three branches.")
        self.assertEqual(data["mode"], "groq")
        self.assertEqual(data["model"], MODEL)
        self.assertEqual({key: data[key] for key in FEEDBACK}, FEEDBACK)
        self.assertEqual(data["note"], interview.GROQ_NOTE)
        payload = self.calls[0]
        self.assertEqual(payload["response_format"], {"type": "json_object"})
        self.assertNotIn("tools", payload)
        sent = json.loads(payload["messages"][1]["content"])
        self.assertEqual(set(sent), {"role", "question", "answer", "evidence"})
        self.assertNotIn("jane@example.com", sent["answer"])
        self.assertNotIn("712 345 678", sent["answer"])
        self.assertIn("[email removed]", sent["answer"])
        self.assertIn("UNTRUSTED DATA", payload["messages"][0]["content"])

    def test_invalid_ai_feedback_falls_back_to_checklist(self):
        cases = {
            "score out of range": {**FEEDBACK, "score": 6},
            "boolean score": {**FEEDBACK, "score": True},
            "invented number": {**FEEDBACK, "stronger_answer": "Action: I reduced errors by 40% across 3 branches.\nResult: [your result]"},
            "invented tool": {**FEEDBACK, "stronger_answer": "Action: I automated the check with Python and SQL.\nResult: [your result]"},
            "too many strengths": {**FEEDBACK, "strengths": ["a", "b", "c", "d"]},
            "missing key": {key: value for key, value in FEEDBACK.items() if key != "verdict"},
            "bad star": {**FEEDBACK, "star": {"situation": True}},
            "promise": {**FEEDBACK, "verdict": "You will get the job with this answer."},
            "not json": "Great answer!",
        }
        for name, generated in cases.items():
            with self.subTest(name):
                self.assert_checklist(self.feedback(generated))

    def test_missing_key_returns_checklist_without_http(self):
        with patch.dict(os.environ, {"NVIDIA_API_KEY": "", "GROQ_API_KEY": ""}), patch("njia.groq_client.httpx.AsyncClient") as client:
            response = self.client.post("/api/interview/feedback", json=self.body)
            client.assert_not_called()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assert_checklist(data)
        self.assertTrue(data["star"]["situation"] and data["star"]["action"])
        self.assertNotIn("jane@example.com", json.dumps(data))

    def test_checklist_scores_thin_answers_lower(self):
        thin = interview.checklist_feedback("Tell me about a data error.", "I think data is important for business.")
        rich = interview.checklist_feedback(self.body["question"], ANSWER + " As a result the supervisor fixed the records, which I learned to check weekly. " * 2)
        self.assertLess(thin["score"], rich["score"])


if __name__ == "__main__":
    unittest.main()
