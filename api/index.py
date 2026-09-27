"""Vercel's supported file-based ASGI entrypoint; keep the app in its package."""

import os

os.environ.setdefault("NJIA_AI_PROVIDER", "offline")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

from njia.app import app  # noqa: E402, F401
