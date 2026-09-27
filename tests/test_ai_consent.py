import os
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from njia.app import app


class AIConsentTests(unittest.TestCase):
    def test_remote_requires_consent_and_curated_is_available(self):
        payload = {"country": "Kenya", "role": "Data Analyst", "skills": ["sql"], "hours": 5}
        with patch.dict(os.environ, {"NJIA_AI_PROVIDER": "groq", "GROQ_API_KEY": "test-key"}), patch("njia.coaching.generate_plan") as generate:
            client = TestClient(app)
            self.assertEqual(client.post("/api/plan", json=payload).status_code, 422)
            response = client.post("/api/plan", json={**payload, "use_ai": False})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["mode"], "curated")
            generate.assert_not_called()
