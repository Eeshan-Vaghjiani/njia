$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath "$PSScriptRoot\.venv\Scripts\python.exe")) {
    throw "Create the environment first: python -m venv .venv; then .\.venv\Scripts\python.exe -m pip install -r requirements.txt"
}
& "$PSScriptRoot\.venv\Scripts\python.exe" -m uvicorn njia.app:app --app-dir "$PSScriptRoot" --host 127.0.0.1 --port 8000 --no-access-log
