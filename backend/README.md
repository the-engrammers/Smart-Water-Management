# Backend

## What it does
- Exposes FastAPI endpoints for health check and sensor ingestion.
- Detects leaks based on sensor `status` or `flow_rate >= 40`.
- Sends Discord alerts and logs alerts to `frontend/alert_logs.csv`.

## Run
1. Install dependencies:
	```bash
	pip install -r requirements.txt
	```
2. Start API from project root:
	```bash
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
	```
3. Test health endpoint:
	- `GET http://localhost:8000/health`

