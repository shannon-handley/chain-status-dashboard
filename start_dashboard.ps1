$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $root ".venv\Scripts\python.exe"
$venvStreamlit = Join-Path $root ".venv\Scripts\streamlit.exe"

if (-not (Test-Path $venvPython)) {
    python -m venv (Join-Path $root ".venv")
}

& $venvPython -m pip install -r (Join-Path $root "requirements.txt")
& $venvStreamlit run (Join-Path $root "app.py") --server.address 0.0.0.0 --server.port 8765
