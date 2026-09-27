FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    NJIA_AI_PROVIDER=offline \
    OPENBLAS_NUM_THREADS=1 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    PORT=10000

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir --only-binary=:all: -r requirements.txt \
    && groupadd --gid 10001 njia \
    && useradd --uid 10001 --gid njia --no-log-init --create-home njia

# Deliberate allowlist: never copy the workspace, .env, CVs, or artifacts.
COPY njia/__init__.py njia/app.py njia/assessment.py njia/coaching.py njia/engine.py njia/uploads.py njia/advisor.py njia/groq_client.py njia/questions.py njia/jobs.py njia/interview.py ./njia/
COPY static/index.html static/app.js static/styles.css static/sample-cv.txt static/coach.html static/coach.js static/coach.css static/followup.css static/jobs.js static/jobs.css static/interview.js static/interview.css ./static/
COPY data/africa_jobs_subset.jsonl ./data/africa_jobs_subset.jsonl

USER 10001:10001
EXPOSE 10000

HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + (os.environ.get('PORT') or '10000') + '/api/health', timeout=4)"

# exec forwards signals; the shell expands the host-assigned PORT at runtime.
# Render overrides FORWARDED_ALLOW_IPS for its trusted ingress proxy.
CMD ["sh", "-c", "exec python -m uvicorn njia.app:app --host 0.0.0.0 --port \"${PORT:-10000}\" --workers 1 --proxy-headers --forwarded-allow-ips \"${FORWARDED_ALLOW_IPS:-127.0.0.1}\""]
