import copy
import json
import os
import unittest
from unittest.mock import patch

import httpx

from njia import coaching


class HostedAITests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {
            "NJIA_AI_PROVIDER": "groq", "GROQ_API_KEY": "test-only-secret",
            "GROQ_MODEL": "", "NJIA_OLLAMA_URL": "https://untrusted.example",
        })
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.analysis = {
            "gaps": [{"id": "python", "count": 5, "demand_pct": 50}],
            "skills": [], "sample_size": 10, "role": "Data Analyst", "scope": "Kenya",
            "cv": "PRIVATE_CV_CANARY", "text": "PRIVATE_TEXT_CANARY",
            "name": "PRIVATE_NAME_CANARY", "email": "private@example.com",
            "jobs": [{"title": "PRIVATE_JOB_CANARY"}],
        }
        self.generated = {"weeks": [{
            "title": f"Practice session {i}", "tasks": ["Read an example", "Build an exercise", "Reflect locally"],
            "deliverable": "A reproducible exercise",
        } for i in range(4)]}
        self.curated = coaching.offline_plan(self.analysis, 5)
        self.client_class = httpx.AsyncClient

    def envelope(self, content=None, **extra):
        return {"model": coaching.GROQ_DEFAULT_MODEL, "choices": [{
            "finish_reason": "stop", "message": {"content": json.dumps(self.generated) if content is None else content},
        }], **extra}

    async def generate(self, handler):
        # A real httpx client/MockTransport exercises URL, headers, streaming,
        # status handling and JSON encoding without any network inference.
        with patch("njia.coaching.httpx.AsyncClient", side_effect=lambda **kwargs: self.client_class(
            transport=httpx.MockTransport(handler), **kwargs,
        )):
            return await coaching.generate_plan(self.analysis, 5)

    def assert_curated(self, result):
        self.assertEqual(result["mode"], "curated")
        self.assertIsNone(result["model"])
        self.assertEqual(result["weeks"], self.curated["weeks"])
        self.assertIn("curated", result["note"])
        self.assertNotIn("test-only-secret", json.dumps(result))

    async def test_success_preserves_grounded_fields_and_identifies_provider_model(self):
        calls = []

        def handler(request):
            calls.append(request)
            self.assertEqual(str(request.url), "https://api.groq.com/openai/v1/chat/completions")
            self.assertEqual(request.method, "POST")
            self.assertEqual(request.headers["Authorization"], "Bearer test-only-secret")
            payload = json.loads(request.content)
            self.assertEqual(payload["model"], coaching.GROQ_DEFAULT_MODEL)
            self.assertEqual(payload["response_format"], {"type": "json_object"})
            self.assertFalse(payload["stream"])
            self.assertLessEqual(payload["max_completion_tokens"], 2000)
            return httpx.Response(200, json=self.envelope())

        result = await self.generate(handler)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["mode"], "groq")
        self.assertEqual(result["model"], coaching.GROQ_DEFAULT_MODEL)
        self.assertIn("Groq", result["note"])
        self.assertIn(result["model"], result["note"])
        for original, actual, generated in zip(self.curated["weeks"], result["weeks"], self.generated["weeks"]):
            self.assertEqual(actual, {**original, **generated})

    async def test_privacy_payload_is_only_allowlisted_curriculum(self):
        self.analysis["gaps"][0]["cv"] = "NESTED_PRIVATE_CANARY"

        def handler(request):
            payload = json.loads(request.content)
            prompt = payload["messages"]
            self.assertEqual([m["role"] for m in prompt], ["system", "user"])
            self.assertIn("Do not generate statistical claims", prompt[0]["content"])
            curriculum = json.loads(prompt[1]["content"])
            self.assertEqual(set(curriculum), {"weeks"})
            for week in curriculum["weeks"]:
                self.assertEqual(set(week), {"week", "skill", "title", "tasks", "deliverable", "hours"})
            for secret in ("PRIVATE", "private@example.com", "Kenya", "Data Analyst", "demand_pct", "test-only-secret"):
                self.assertNotIn(secret, request.content.decode())
            return httpx.Response(200, json=self.envelope())

        self.assertEqual((await self.generate(handler))["mode"], "groq")

    async def test_missing_or_blank_key_never_creates_http_client(self):
        for key in (None, "", "  "):
            with self.subTest(key=key), patch.dict(os.environ):
                if key is None:
                    os.environ.pop("GROQ_API_KEY", None)
                else:
                    os.environ["GROQ_API_KEY"] = key
                with patch("njia.coaching.httpx.AsyncClient") as client:
                    result = await coaching.generate_plan(self.analysis, 5)
                    client.assert_not_called()
                self.assert_curated(result)
                self.assertIn("key missing", result["note"])

    async def test_http_errors_and_redirects_fall_back_without_retry_or_secret_echo(self):
        for status in (401, 403, 429, 500, 503, 307):
            calls = []

            def handler(request):
                calls.append(request)
                return httpx.Response(status, text="test-only-secret private@example.com",
                                      headers={"location": "https://untrusted.example", "retry-after": "120"})

            with self.subTest(status=status):
                result = await self.generate(handler)
                self.assert_curated(result)
                self.assertNotIn("private@example.com", json.dumps(result))
                self.assertEqual(len(calls), 1)

    async def test_connection_and_timeout_errors_fall_back(self):
        for error in (httpx.ConnectError, httpx.ReadTimeout):
            def handler(request):
                raise error("test-only-secret", request=request)

            with self.subTest(error=error):
                self.assert_curated(await self.generate(handler))

    async def test_wrong_response_envelopes_and_truncated_completions(self):
        invalid = [None, [], {}, {"choices": []}, {"choices": [None]}, {"choices": "wrong"},
                   {"choices": [{"finish_reason": "stop", "message": []}]},
                   self.envelope(choices=[{"finish_reason": "length", "message": {"content": json.dumps(self.generated)}}]),
                   self.envelope(model=None), self.envelope(content="not JSON")]
        for envelope in invalid:
            with self.subTest(envelope=envelope):
                self.assert_curated(await self.generate(lambda request: httpx.Response(200, content=json.dumps(envelope))))

    async def test_invalid_generated_shapes_and_bounds_are_atomic(self):
        invalid = [[], {"weeks": []}, {"weeks": [None] * 4}, {"weeks": self.generated["weeks"] * 2}]
        for field, value in (("title", 5), ("title", "  "), ("title", "x" * 401),
                             ("deliverable", ""), ("deliverable", "x" * 401),
                             ("tasks", "wrong"), ("tasks", ["Read"] * 2),
                             ("tasks", ["Read", None, "Build"]), ("tasks", [" "] * 3),
                             ("tasks", ["x" * 701] * 3), ("why", "invented statistics"),
                             ("resource", {"url": "https://untrusted.example"})):
            generated = copy.deepcopy(self.generated)
            # Last-week failures must never leave earlier weeks AI-rewritten.
            generated["weeks"][-1][field] = value
            invalid.append(generated)
        for generated in invalid:
            with self.subTest(generated=generated):
                self.assert_curated(await self.generate(lambda request: httpx.Response(200, json=self.envelope(json.dumps(generated)))))

    async def test_oversized_deep_duplicate_and_non_json_output(self):
        bodies = [b"x" * (coaching.MAX_HOSTED_RESPONSE_BYTES + 1), b"not json", b"\xff",
                  ("[" * 2000 + "]" * 2000).encode()]
        for content in (" " * (coaching.MAX_HOSTED_CONTENT_CHARS + 1),
                        '{"weeks": [], "weeks": ' + json.dumps(self.generated["weeks"]) + '}',
                        "[" * 2000 + "]" * 2000):
            bodies.append(json.dumps(self.envelope(content)).encode())
        for body in bodies:
            with self.subTest(size=len(body)):
                self.assert_curated(await self.generate(lambda request: httpx.Response(200, content=body)))

    async def test_configurable_model_and_reported_model(self):
        def handler(request):
            self.assertEqual(json.loads(request.content)["model"], "custom-model")
            return httpx.Response(200, json=self.envelope(model="reported-model"))

        with patch.dict(os.environ, {"GROQ_MODEL": "custom-model"}):
            self.assertEqual(coaching.provider_status()["model"], "custom-model")
            result = await self.generate(handler)
        self.assertEqual(result["model"], "reported-model")
        self.assertIn("reported-model", result["note"])

    async def test_public_capabilities_are_side_effect_free_and_never_expose_key(self):
        with patch("njia.coaching.httpx.AsyncClient") as client:
            status = coaching.provider_status()
            self.assertEqual(status["provider"], "groq")
            self.assertTrue(status["is_remote"])
            self.assertTrue(status["configured"])
            self.assertIn("availability checked when used", status["label"])
            self.assertNotIn("test-only-secret", json.dumps(status))
            with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
                status = coaching.provider_status()
                self.assertTrue(status["is_remote"])
                self.assertFalse(status["configured"])
                self.assertIn("unavailable", status["label"])
            client.assert_not_called()

    async def test_offline_unknown_and_ollama_capabilities_stay_local(self):
        for provider in ("offline", "unknown", "ollama"):
            with self.subTest(provider=provider), patch.dict(os.environ, {"NJIA_AI_PROVIDER": provider}):
                status = coaching.provider_status()
                self.assertFalse(status["is_remote"])
                self.assertEqual(status["provider"], "ollama" if provider == "ollama" else "offline")
                if provider != "ollama":
                    with patch("njia.coaching.httpx.AsyncClient") as client:
                        self.assertEqual(await coaching.generate_plan(self.analysis, 5), self.curated)
                        client.assert_not_called()


if __name__ == "__main__":
    unittest.main()
