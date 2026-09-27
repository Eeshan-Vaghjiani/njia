import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from njia.app import app


class AdvisorAPITests(unittest.TestCase):
    def test_consent_and_whitespace_never_reach_ai(self):
        client = TestClient(app)
        payload = {"text": "Skills SQL Python", "country": "Kenya", "role": "Data Analyst", "consent": False}
        with patch("njia.advisor.assess_cv") as model:
            self.assertEqual(client.post("/api/advise", json=payload).status_code, 422)
            self.assertEqual(client.post("/api/advise", json={**payload, "consent": True, "text": " "*20}).status_code, 422)
            model.assert_not_called()
