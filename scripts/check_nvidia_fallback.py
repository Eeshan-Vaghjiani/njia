"""Real local API smoke check: at most two NVIDIA requests, synthetic CV only.

Run with .venv/Scripts/python.exe -B scripts/check_nvidia_fallback.py.
The application loads dotenv; credentials and generated prose are never printed.
"""
import json
import os
from pathlib import Path
import re
import sys
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import httpx
from fastapi.testclient import TestClient

from njia.app import app  # Use the application's existing dotenv loading.
from njia import advisor, engine, groq_client, questions

OUTPUT = ROOT / "artifacts" / "nvidia-fallback-results.json"
SYNTHETIC_CV = (
    "Built a Power BI dashboard comparing synthetic sales by branch.\n"
    "Used SQL to join two synthetic sales tables.\n"
    "Prepared a monthly sales summary for a course project."
)


def require(condition):
    if not condition:
        raise ValueError("Fallback result failed validation")


def validate(result, feature):
    require(result.get("mode") == "nvidia")
    require(isinstance(result.get("model"), str))
    require(re.fullmatch(r"[A-Za-z0-9._/-]{1,200}", result["model"]) is not None)
    allowed = set(engine.vocabulary())
    if feature == "questions":
        items = result["questions"]
        require(questions.MIN_AI_QUESTIONS <= len(items) <= questions.MAX_QUESTIONS)
        require([item["id"] for item in items] == [f"q{i + 1}" for i in range(len(items))])
        for item in items:
            require(set(item) == {"id", "type", "skill", "question", "why", "options"})
            require(item["type"] in {"skill", "detail"})
            require(all(isinstance(item[k], str) and item[k].strip() for k in ("question", "why")))
            if item["type"] == "skill":
                require(item["skill"] in allowed and item["options"] == list(advisor.SKILL_OPTIONS))
            else:
                require(item["options"] == [])
    else:
        require([item["day"] for item in result["seven_day_plan"]] == list(range(1, 8)))
        for item in result["seven_day_plan"]:
            require(all(isinstance(item[k], str) and item[k].strip() for k in ("action", "deliverable")))
        require(bool(result["summary"].strip()))
        require(all(result["interview"][k].strip() for k in ("question", "what_good_looks_like")))
        require(bool(result["strengths"]))
        for item in result["strengths"]:
            require(item["skill"] in allowed)
            require(advisor._normal(item["evidence"]) in advisor._normal(SYNTHETIC_CV))
        require(set(result["suggested_skills"]) <= allowed)


def main():
    requests = 0
    original = httpx.AsyncHTTPTransport.handle_async_request

    async def bounded_request(transport, request):
        nonlocal requests
        # Guard the real transport without inspecting headers or credentials.
        if (requests >= 2 or request.method != "POST"
                or str(request.url) != groq_client.NVIDIA_ENDPOINT):
            raise RuntimeError("Outbound request outside smoke-check budget")
        requests += 1
        return await original(transport, request)

    evidence = {"groq_forced_unavailable": True, "request_limit": 2, "results": []}
    payload = {"text": SYNTHETIC_CV, "country": "Kenya", "role": "Data Analyst", "consent": True}
    with patch.dict(os.environ, {"GROQ_API_KEY": ""}), patch.object(
        httpx.AsyncHTTPTransport, "handle_async_request", bounded_request
    ), TestClient(app) as client:
        for feature, endpoint in (("questions", "/api/questions"), ("advisor", "/api/advise")):
            started = time.perf_counter()
            before = requests
            record = {"feature": feature, "mode": None, "model": None, "json_validated": False}
            try:
                response = client.post(endpoint, json=payload)
                require(response.status_code == 200)
                body = groq_client.loads(response.content)
                result = body if feature == "questions" else body["advisor"]
                # Only allow known modes and a model identifier into the artifact.
                mode, model = result.get("mode"), result.get("model")
                record["mode"] = mode if mode in {"nvidia", "groq", "curated"} else None
                record["model"] = model if isinstance(model, str) and model == groq_client.fallback_model() else None
                record["question_count" if feature == "questions" else "day_count"] = len(
                    result["questions" if feature == "questions" else "seven_day_plan"]
                )
                validate(result, feature)
                require(requests - before == 1)
                record["json_validated"] = True
            except Exception as error:
                # Exception messages may contain provider output; retain only the class.
                record["error_type"] = type(error).__name__
            record["elapsed_seconds"] = round(time.perf_counter() - started, 3)
            record["nvidia_requests"] = requests - before
            evidence["results"].append(record)
    evidence["nvidia_requests"] = requests
    evidence["passed"] = requests == 2 and all(item["json_validated"] for item in evidence["results"])
    serialized = json.dumps(evidence, separators=(",", ":"), allow_nan=False)
    OUTPUT.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
