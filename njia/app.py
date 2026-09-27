from contextlib import asynccontextmanager
import time
import os
from typing import Annotated, Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import assessment, coaching, engine, uploads, advisor, questions, jobs, interview

load_dotenv(engine.ROOT / ".env")


@asynccontextmanager
async def lifespan(app):
    engine.corpus()
    engine.vocabulary()
    yield


app = FastAPI(title="Njia career coach", version="1.1.0", lifespan=lifespan)
app.include_router(uploads.router)
app.include_router(questions.router)
app.include_router(jobs.router)
app.include_router(interview.router)


@app.middleware("http")
async def local_headers(request: Request, call_next):
    # Serve a single origin; a trusted deployment URL can account for TLS termination.
    origin = request.headers.get("origin")
    allowed_origins = {str(request.base_url).rstrip("/")}
    for name in ("VERCEL_URL", "VERCEL_PROJECT_PRODUCTION_URL"):
        if os.getenv(name):
            allowed_origins.add("https://" + os.environ[name])
    allowed_origins.update(s.strip().rstrip("/") for s in os.getenv("NJIA_PUBLIC_ORIGINS", "").split(",") if s.strip())
    if request.method == "POST" and origin and origin not in allowed_origins:
        return JSONResponse({"detail": "Use the same origin as the application."}, status_code=403)
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    return response


class ExtractRequest(BaseModel):
    text: str = Field(min_length=10, max_length=15000)
    consent: bool


class Answer(BaseModel):
    id: str = Field(max_length=10)
    type: Literal["skill", "detail"]
    skill: str | None = Field(default=None, max_length=100)
    question: str = Field(max_length=300)
    answer: str = Field(max_length=400)


class AdvisorRequest(ExtractRequest):
    country: str = Field(max_length=80)
    role: str = Field(max_length=80)
    answers: list[Answer] = Field(default_factory=list, max_length=6)


class AnalysisRequest(BaseModel):
    country: str = Field(max_length=80)
    role: str = Field(max_length=80)
    skills: list[str] = Field(max_length=100)


class PlanRequest(AnalysisRequest):
    hours: int = Field(default=5, ge=1, le=20)
    use_ai: bool = True
    ai_consent: bool = False


class GradeRequest(BaseModel):
    skill: str = Field(max_length=80)
    answers: list[Annotated[int, Field(ge=0, le=2)]] = Field(min_length=3, max_length=3)


def validate_market(body):
    meta = engine.metadata()
    if body.country not in {c["name"] for c in meta["countries"]} or body.role not in meta["roles"]:
        raise HTTPException(422, "Choose a country and role from the available dataset.")
    if any(s not in engine.vocabulary() for s in body.skills):
        raise HTTPException(422, "One or more skills are outside the dataset vocabulary.")
    return sorted(set(body.skills))


@app.get("/api/health")
def health():
    return {"status": "ok", "postings": len(engine.corpus()), "ai": coaching.provider_status()}


@app.get("/api/meta")
def meta():
    return {**engine.metadata(), "ai": coaching.provider_status(), "assessment_skills": list(assessment.BANK)}


@app.post("/api/extract")
def extract(body: ExtractRequest):
    if not body.consent:
        raise HTTPException(422, "Please agree to in-memory server processing, or choose skills manually.")
    if len(body.text.strip()) < 10:
        raise HTTPException(422, "Add a short description of your experience.")
    start = time.perf_counter()
    skills = engine.extract_skills(body.text)
    return {"skills": skills, "mode": "lexicon", "elapsed_ms": round((time.perf_counter()-start)*1000, 1), "note": "Local keyword and alias extraction, not a language model. Review every suggestion; implied skills and complex negations can be missed. CV text is not stored or sent to a model."}


@app.post("/api/analyze")
def analyze(body: AnalysisRequest):
    start = time.perf_counter()
    result = engine.analyze(body.country, body.role, validate_market(body))
    return {**result, "elapsed_ms": round((time.perf_counter()-start)*1000, 1)}


@app.post("/api/advise")
async def advise(body: AdvisorRequest):
    if not body.consent:
        raise HTTPException(422, "Consent is required to send redacted CV text to the AI provider. You can use the manual skills tool instead.")
    if len(body.text.strip()) < 10:
        raise HTTPException(422, "Add at least 10 characters about your experience.")
    validate_market(AnalysisRequest(country=body.country, role=body.role, skills=[]))
    start = time.perf_counter()
    result = await advisor.assess_cv(body.text, body.country, body.role,
                                     answers=[item.model_dump() for item in body.answers] or None)
    market = engine.analyze(body.country, body.role, result["suggested_skills"])
    return {"advisor": result, "market": market, "elapsed_ms": round((time.perf_counter()-start)*1000, 1)}


@app.post("/api/plan")
async def plan(body: PlanRequest):
    result = engine.analyze(body.country, body.role, validate_market(body))
    if not body.use_ai:
        return coaching.offline_plan(result, body.hours)
    provider = coaching.provider_status()
    if provider.get("is_remote") and provider.get("configured") and not body.ai_consent:
        raise HTTPException(422, "Agree to send structured skill curriculum to the AI provider, or choose the curated plan.")
    return await coaching.generate_plan(result, body.hours)


@app.get("/api/assessment/{skill}")
def get_assessment(skill: str):
    if skill not in assessment.BANK:
        raise HTTPException(404, "No practice check is available for this skill yet.")
    return assessment.questions(skill)


@app.post("/api/assessment/grade")
def grade(body: GradeRequest):
    if body.skill not in assessment.BANK:
        raise HTTPException(422, "Choose an available practice check.")
    return assessment.grade(body.skill, body.answers)


@app.get("/")
def index():
    return FileResponse(engine.ROOT / "static/coach.html")


@app.get("/classic")
def classic():
    return FileResponse(engine.ROOT / "static/index.html")


app.mount("/static", StaticFiles(directory=engine.ROOT / "static"), name="static")
