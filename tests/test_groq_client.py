import json
import os
import unittest
from unittest.mock import patch

import httpx

from njia import groq_client


class GroqClientTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {"GROQ_API_KEY": "client-test-secret", "GROQ_MODEL": "",
                                                   "NJIA_ADVISOR_MODEL": "", "NJIA_SEARCH_MODEL": ""})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.client_class = httpx.AsyncClient
        self.payloads = []

    async def call(self, response, **kwargs):
        def handler(request):
            self.payloads.append(json.loads(request.content))
            return response(request) if callable(response) else response

        with patch("njia.groq_client.httpx.AsyncClient", side_effect=lambda **options: self.client_class(
                transport=httpx.MockTransport(handler), **options)):
            return await groq_client.chat([{"role": "user", "content": "hi"}], **kwargs)

    @staticmethod
    def envelope(content='{"ok": true}', finish="stop", **message):
        return httpx.Response(200, json={"model": "openai/gpt-oss-20b", "choices": [
            {"finish_reason": finish, "message": {"role": "assistant", "content": content, **message}}]})

    async def test_json_mode_uses_default_model_and_low_reasoning(self):
        content, message, model = await self.call(self.envelope())
        self.assertEqual((content, model), ('{"ok": true}', "openai/gpt-oss-20b"))
        payload = self.payloads[0]
        self.assertEqual(payload["model"], groq_client.DEFAULT_MODEL)
        self.assertEqual(payload["response_format"], {"type": "json_object"})
        self.assertEqual(payload["reasoning_effort"], "low")
        self.assertNotIn("tools", payload)

    async def test_browser_search_uses_search_model_without_json_mode(self):
        await self.call(self.envelope("text"), tools=groq_client.BROWSER_SEARCH, model=groq_client.search_model())
        payload = self.payloads[0]
        self.assertEqual(payload["model"], "openai/gpt-oss-120b")
        self.assertEqual(payload["tools"], [{"type": "browser_search"}])
        self.assertEqual(payload["tool_choice"], "required")
        self.assertEqual(payload["temperature"], 1.0)
        self.assertNotIn("response_format", payload)

    async def test_json_calls_stay_low_temperature(self):
        await self.call(self.envelope())
        self.assertEqual(self.payloads[0]["temperature"], 0.2)

    def test_search_model_is_separate_and_configurable(self):
        self.assertNotEqual(groq_client.search_model(), groq_client.model_name())
        with patch.dict(os.environ, {"NJIA_SEARCH_MODEL": "openai/gpt-oss-20b"}):
            self.assertEqual(groq_client.search_model(), "openai/gpt-oss-20b")

    async def test_failures_raise_generic_provider_error(self):
        cases = [httpx.Response(429, json={"error": {"message": "rate limit"}}),
                 self.envelope(finish="length"), self.envelope(content="  "),
                 self.envelope(content="client-test-secret")]
        for response in cases:
            with self.subTest(status=response.status_code):
                with self.assertRaises(groq_client.ProviderError) as caught:
                    await self.call(response)
                self.assertNotIn("client-test-secret", str(caught.exception))
                self.assertNotIn("rate limit", str(caught.exception))

    async def test_missing_key_never_calls_provider(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            with self.assertRaises(groq_client.ProviderError):
                await self.call(self.envelope())
        self.assertEqual(self.payloads, [])

    def test_loose_json_accepts_fences_and_prose_but_stays_strict(self):
        self.assertEqual(groq_client.loose_json('Here:\n```json\n{"a": 1}\n```'), {"a": 1})
        self.assertEqual(groq_client.loose_json('Result {"a": [1, 2]} done'), {"a": [1, 2]})
        for bad in ('{"a": 1, "a": 2}', "no json", '{"a": NaN}', ""):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                groq_client.loose_json(bad)

    def test_evidence_urls_are_normalized_from_nested_tool_output(self):
        message = {"executed_tools": [{"output": "See https://www.Example.com/jobs/1/ and http://example.org/a?b=1).",
                                       "search_results": {"results": [{"url": "https://brightermonday.co.ke/listings/x"}]}}]}
        self.assertEqual(groq_client.evidence_urls(message), {
            "https://example.com/jobs/1", "https://example.org/a?b=1", "https://brightermonday.co.ke/listings/x"})
        self.assertIsNone(groq_client.normalize_url("javascript:alert(1)"))
        self.assertIsNone(groq_client.normalize_url("https://user:pass@example.com/"))
        self.assertEqual(groq_client.evidence_urls({"content": "https://not-tool-output.example"}), set())


if __name__ == "__main__":
    unittest.main()
