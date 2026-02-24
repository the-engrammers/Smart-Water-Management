# Simulator

## What it does
- Reads historical rows from `data/Aquifer_Petrignano.csv`.
- Sends periodic sensor payloads to `POST /ingest`.

## Run
1. Ensure backend API is running on port `8000`.
2. Start simulator from project root:
	 ```bash
	 python simulator/stream_data.py
	 ```

## Optional
- Override API endpoint:
	- Windows PowerShell:
		```powershell
		$env:API_URL = "http://localhost:8000/ingest"
		```

