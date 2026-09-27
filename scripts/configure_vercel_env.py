"""Copy only approved runtime values into Vercel via stdin, never CLI arguments."""
import os
from pathlib import Path
import shutil
import subprocess
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent
values = dotenv_values(ROOT / ".env")
approved = {
    "GROQ_API_KEY": values.get("GROQ_API_KEY"),
    "NJIA_AI_PROVIDER": "groq",
    "GROQ_MODEL": "openai/gpt-oss-20b",
    "NJIA_PUBLIC_ORIGINS": "https://gomycode-2026.vercel.app",
    "OPENBLAS_NUM_THREADS": "1",
}
cli = shutil.which("vercel.cmd" if os.name == "nt" else "vercel")
if not cli:
    raise SystemExit("Vercel CLI not found")
for name, value in approved.items():
    if not value:
        raise SystemExit(f"Missing {name}; no credential value printed")
    command = [cli, "env", "add", name, "production"]
    if name == "GROQ_API_KEY":
        command.append("--sensitive")
    result = subprocess.run(command, input=value, text=True, capture_output=True, cwd=ROOT)
    print(f"{name}: {'configured' if result.returncode == 0 else 'failed (check Vercel environment settings)'}")
    if result.returncode:
        raise SystemExit(result.returncode)
