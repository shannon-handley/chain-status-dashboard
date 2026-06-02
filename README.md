# Chain Status Dashboard

Streamlit dashboard for chain channel status, project completion, active issues, and upcoming chain migrations.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\streamlit.exe run app.py --server.address 0.0.0.0 --server.port 8765
```

## Deploy

Deploy `app.py` from this repository with Streamlit Community Cloud or an internal Streamlit host.
