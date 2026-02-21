# Import FastAPI framework to create the web server and API endpoints
# Import BaseModel from Pydantic to define and validate the data structure
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Try importing the Discord alert function from different possible locations
try:
    from backend.alert_service import send_discord_alert
except ImportError:
    from alert_service import send_discord_alert


# Threshold value to detect abnormal flow rate (possible leak)
LEAK_FLOW_RATE_THRESHOLD = 40.0


# Create an instance of FastAPI
# This object is the main entry point of the application
app = FastAPI()


# Define the data model (Data Contract) for incoming sensor data
# This ensures the incoming JSON has the correct structure and types
class SensorData(BaseModel):

    # device_id must not be empty
    device_id: str = Field(..., min_length=1)

    # timestamp is required and must not be empty
    timestamp: str = Field(..., min_length=1)

    # water_level cannot be negative
    water_level: float = Field(..., ge=0)

    # temperature can be negative
    temperature: float

    # flow_rate must be strictly positive
    flow_rate: float = Field(..., gt=0)

    # status is optional
    status: Optional[str] = None


# Health check endpoint
# Accessible via GET request at /health
@app.get("/health")
def health_check():
    return {"status": "Server running"}


# Data ingestion endpoint
# Receives sensor data via POST request at /ingest
@app.post("/ingest")
def ingest(data: SensorData):

    # Print received data (for debugging)
    print(data)

    # Leak detection logic
    leak_by_status = (data.status or "").strip().lower() == "leak"
    leak_by_flow = data.flow_rate >= LEAK_FLOW_RATE_THRESHOLD
    leak_detected = leak_by_status or leak_by_flow

    alert_sent = False

    # If leak detected, send alert
    if leak_detected:
        alert_payload = {
            "device_id": data.device_id,
            "flow_rate": data.flow_rate,
            "water_level": data.water_level,
            "temperature": data.temperature,
            "status": "Leak",
            "timestamp": data.timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            alert_sent = send_discord_alert(alert_payload)
        except Exception as e:
            print("Discord error:", e)
            alert_sent = False

    # Return confirmation response
    return {
        "message": "Data received",
        "alert_sent": alert_sent,
        "leak_detected": leak_detected
    }
