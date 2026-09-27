"""Shared, bounded Groq chat-completions client for Njia's AI features.

Callers own consent and choose exactly which fields are sent. This module never
logs prompts, CV text, provider error bodies or credentials. One request per
call: no retries and no redirects.
"""
import asyncio
import json
import os
import re
from urllib.parse import urlsplit, urlunsplit

import httpx
from dotenv import load_dotenv

from . import engine

load_dotenv(engine.ROOT / ".env")

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-oss-20b"
DEFAULT_SEARCH_MODEL = "openai/gpt-oss-120b"
MAX_RESPONSE_BYTES = 512 * 1024
URL_PATTERN = re.compile(r"https?://[^\s<>\"'()\[\]{}|\\^`]+", re.I)
BROWSER_SEARCH = [{"type": "browser_search"}]


class ProviderError(Exception):
    """Generic provider failure. The message never includes provider output."""


def configured() -> bool:
    return bool(os.getenv("GROQ_API_KEY", "").strip())


def model_name() -> str:
    return (os.getenv("NJIA_ADVISOR_MODEL", "").strip()
            or os.getenv("GROQ_MODEL", "").strip() or DEFAULT_MODEL)


def search_model() -> str:
    """Model for token-heavy browser searches.

    Groq's free tier limits tokens per day per model, so web research defaults to
    a different model than the CV brief to keep searches from exhausting it.
    """
    return os.getenv("NJIA_SEARCH_MODEL", "").strip() or DEFAULT_SEARCH_MODEL


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError("Non-finite JSON value")


def loads(content):
    """Strict JSON: duplicate keys and NaN/Infinity are rejected."""
    return json.loads(content, object_pairs_hook=_unique_object, parse_constant=_invalid_constant)


def loose_json(content):
    """Parse one JSON object from model text (browser_search cannot use JSON mode)."""
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Empty content")
    text = content.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S | re.I)
    if fenced:
        text = fenced.group(1)
    else:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("No JSON object")
        text = text[start:end + 1]
    data = loads(text)
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object")
    return data


def normalize_url(url):
    """Comparable https form of a public http(s) URL, or None if unusable."""
    if not isinstance(url, str) or not url.strip() or len(url) > 2000:
        return None
    url = url.strip().rstrip(".,;:!?)]}'\"")
    try:
        parts = urlsplit(url)
        host = parts.hostname
    except ValueError:
        return None
    if parts.scheme.lower() not in {"http", "https"} or not host or parts.username or parts.password:
        return None
    return urlunsplit(("https", host.lower().removeprefix("www."), parts.path.rstrip("/"), parts.query, ""))


def _tool_strings(message):
    stack = [message.get("executed_tools")] if isinstance(message, dict) else []
    while stack:
        value = stack.pop()
        if isinstance(value, str):
            yield value
        elif isinstance(value, dict):
            stack.extend(value.values())
        elif isinstance(value, list):
            stack.extend(value)


def tool_text(message) -> str:
    """Concatenated string output of the provider's executed tools (search evidence)."""
    return "\n".join(_tool_strings(message))


def evidence_urls(message) -> set:
    """Normalized URLs that appear in executed tool output."""
    found = set()
    for value in _tool_strings(message):
        for match in URL_PATTERN.findall(value):
            normal = normalize_url(match)
            if normal:
                found.add(normal)
    return found


async def chat(messages, *, json_mode=True, tools=None, tool_choice="required", max_tokens=2000,
               timeout=45.0, temperature=None, reasoning_effort="low", model=None):
    """One bounded chat completion. Returns ``(content, message, actual_model)``.

    ``tools=BROWSER_SEARCH`` enables Groq's server-side web search; JSON mode is
    then disabled (unsupported with tools), so parse with ``loose_json``.
    Tool calls default to temperature 1.0 (Groq's browser-search setting); at low
    temperature gpt-oss-120b produced unparseable tool calls. JSON calls use 0.2.
    ``model`` overrides the configured advisor model (e.g. ``search_model()``).
    Raises ProviderError for a missing key, transport/HTTP errors, oversized or
    malformed envelopes, credential echoes, and incomplete or empty output.
    """
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        raise ProviderError("Groq API key missing")
    model = model or model_name()
    if temperature is None:
        temperature = 1.0 if tools else 0.2
    payload = {"model": model, "stream": False, "temperature": temperature,
               "max_completion_tokens": max_tokens, "messages": messages}
    if reasoning_effort and model.startswith("openai/gpt-oss-"):
        payload["reasoning_effort"] = reasoning_effort
    if tools:
        payload["tools"] = tools
        if tool_choice:
            payload["tool_choice"] = tool_choice
    elif json_mode:
        payload["response_format"] = {"type": "json_object"}
    try:
        async with asyncio.timeout(timeout):
            async with httpx.AsyncClient(timeout=timeout, trust_env=False, follow_redirects=False) as client:
                async with client.stream("POST", GROQ_ENDPOINT, headers={"Authorization": f"Bearer {key}"},
                                         json=payload) as response:
                    response.raise_for_status()
                    body = bytearray()
                    async for chunk in response.aiter_bytes():
                        if len(body) + len(chunk) > MAX_RESPONSE_BYTES:
                            raise ValueError("Response too large")
                        body.extend(chunk)
        if key.encode() in body:
            raise ValueError("Credential in response")
        envelope = loads(bytes(body))
        if not isinstance(envelope, dict):
            raise ValueError("Invalid provider envelope")
        choices = envelope.get("choices")
        if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
            raise ValueError("Invalid provider choices")
        choice = choices[0]
        message = choice.get("message")
        if choice.get("finish_reason") != "stop" or not isinstance(message, dict):
            raise ValueError("Incomplete completion")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Empty completion")
        actual = envelope.get("model", model)
        if not isinstance(actual, str) or not actual.strip() or len(actual) > 200:
            raise ValueError("Invalid provider model")
        return content, message, actual.strip()
    except (httpx.HTTPError, TimeoutError, ValueError, KeyError, TypeError, RecursionError, UnicodeDecodeError):
        raise ProviderError("Groq unavailable or returned an invalid response") from None
