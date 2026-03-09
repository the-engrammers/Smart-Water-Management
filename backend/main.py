from middleware import limiter
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

from control_service import control_pump, control_valve, get_history
from decision_engine import SensorData as DecisionSensorData, make_irrigation_decision

# Threshold used to detect abnormal flow rate
LEAK_FLOW_RATE_THRESHOLD = 40.0


# Create FastAPI application instance
app = FastAPI()

app.state.limiter = limiter
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


# ===============================
# Control Endpoints
# ===============================

class PumpCommand(BaseModel):
    """Schema for pump requests; expects a JSON object like {"command": "START"}"""
    command: str


class ValveCommand(BaseModel):
    """Schema for valve requests; expects a JSON object like {"command": "OPEN"}"""
    command: str

class IrrigationInput(BaseModel):
    soil_moisture: float
    temperature: float
    humidity: float
    rainfall_forecast: float
    crop_type: str

@app.post("/control/pump")
def pump_control(data: PumpCommand):
    """
    POST Endpoint: Receives a command for the pump.
    Passes the 'command' string to the control_pump logic function.
    """
    return control_pump(data.command)


@app.post("/control/valve")
def valve_control(data: ValveCommand):
    """
    POST Endpoint: Receives a command for the valve.
    Passes the 'command' string to the control_valve logic function.
    """
    return control_valve(data.command)


@app.get("/control/history")
def history():
    """
    GET Endpoint: Returns the full JSON history of all commands executed.
    Useful for monitoring the system state from a web browser or dashboard.
    """
    return get_history()


@app.post("/smart-irrigation")
def smart_irrigation(data: IrrigationInput):
    """
    Intelligent irrigation endpoint.
    Uses rule engine to decide action,
    then triggers hardware automatically.
    """

    # Convert API input into decision engine object
    sensor = DecisionSensorData(**data.dict())

    # Get decision
    decision = make_irrigation_decision(sensor)

    # Execute hardware control automatically
    if decision["action"] == "START_IRRIGATION":
        control_pump("START")
        control_valve("OPEN")
    else:
        control_pump("STOP")
        control_valve("CLOSE")

    return decision
