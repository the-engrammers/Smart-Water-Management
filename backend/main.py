# Import FastAPI framework to create the web server and API endpoints
from fastapi import FastAPI

# Import BaseModel and Field for strict validation
from pydantic import BaseModel, Field

# Import datetime for timestamp handling
from datetime import datetime

# Optional allows some fields to be not required
from typing import Optional

try:
    from backend.alert_service import send_discord_alert
except ImportError:
    from alert_service import send_discord_alert


# Threshold used to detect abnormal flow rate
LEAK_FLOW_RATE_THRESHOLD = 40.0


# Create FastAPI application instance
app = FastAPI()


# ===============================
# Data Model (Strict Validation)
# ===============================
class SensorData(BaseModel):
    # Prevent empty device_id
    device_id: str = Field(..., min_length=1)

    # Optional timestamp (must be valid datetime if provided)
    timestamp: Optional[datetime] = None

    # Water level cannot be negative
    water_level: float = Field(..., ge=0)

    # Temperature required (can add limits later if needed)
    temperature: float

    # Flow rate must be strictly positive
    flow_rate: float = Field(..., gt=0)

    # Optional status
    status: Optional[str] = None


# ===============================
# Health Check Endpoint
# ===============================
@app.get("/health")
def health_check():
    return {"status": "Server running"}


# ===============================
# Data Ingestion Endpoint
# ===============================
@app.post("/ingest")
def ingest(data: SensorData):
    print(data)

    leak_by_status = (data.status or "").strip().lower() == "leak"
    leak_by_flow = data.flow_rate >= LEAK_FLOW_RATE_THRESHOLD
    leak_detected = leak_by_status or leak_by_flow
    alert_sent = False

    if leak_detected:
        alert_payload = {
            "device_id": data.device_id,
            "flow_rate": data.flow_rate,
            "water_level": data.water_level,
            "temperature": data.temperature,
            "status": "Leak",
            "timestamp": (data.timestamp or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            alert_sent = send_discord_alert(alert_payload)
        except Exception as e:
            print("Error sending alert:", e)
            alert_sent = False

    return {
        "message": "Data received",
        "alert_sent": alert_sent,
        "leak_detected": leak_detected
    }
