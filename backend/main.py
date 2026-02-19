# Import FastAPI framework to create the web server and API endpoints
from fastapi import FastAPI

# Import BaseModel from Pydantic to define and validate the data structure
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

try:
    from backend.alert_service import send_discord_alert
except ImportError:
    from alert_service import send_discord_alert


LEAK_FLOW_RATE_THRESHOLD = 40.0


# Create an instance of FastAPI
# This object is the main entry point of the application
app = FastAPI()


# Define the data model (Data Contract) for incoming sensor data
# This ensures the incoming JSON has the correct structure and types
class SensorData(BaseModel):
    device_id: str      # Unique identifier of the sensor device
    timestamp: str      # Time when the data was recorded
    water_level: float  # Current water level measured by the sensor
    flow_rate: float    # Current water flow rate measured by the sensor
    status: Optional[str] = None


# Health check endpoint
# This endpoint is used to verify that the server is running correctly
# It can be accessed via GET request at /health
@app.get("/health")
def health_check():
    # Return a simple status message
    return {"status": "Server running"}


# Data ingestion endpoint
# This endpoint receives sensor data via POST request at /ingest
# FastAPI automatically validates the incoming JSON using SensorData model
@app.post("/ingest")
def ingest(data: SensorData):
    
    # Print the received data to the console (for debugging and monitoring)
    print(data)

    leak_by_status = (data.status or "").strip().lower() == "leak"
    leak_by_flow = data.flow_rate >= LEAK_FLOW_RATE_THRESHOLD
    leak_detected = leak_by_status or leak_by_flow
    alert_sent = False

    if leak_detected:
        alert_payload = {
            "device_id": data.device_id,
            "flow_rate": data.flow_rate,
            "status": "Leak",
            "timestamp": data.timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        alert_sent = send_discord_alert(alert_payload)

    # Return a confirmation response to the sender
    return {"message": "Data received", "alert_sent": alert_sent, "leak_detected": leak_detected}
