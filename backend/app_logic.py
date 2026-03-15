from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import sys
import os

# 1. Database Configuration
# This points to your database folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.connection import SessionLocal

# 2. Service Imports
try:
    from alert_service import send_discord_alert
except ImportError:
    # Fallback if the path is different
    def send_discord_alert(payload): return False

from control_service import control_pump, control_valve, get_history

# ===============================
# APP INITIALIZATION
# ===============================
app = FastAPI(title="Smart Water Management System")

# Database Session Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===============================
# DATA MODELS
# ===============================
class SensorData(BaseModel):
    device_id: str
    water_level: float
    temperature: float
    flow_rate: float
    timestamp: Optional[datetime] = None
    status: Optional[str] = None

class IrrigationInput(BaseModel):
    soil_moisture: float
    temperature: float
    humidity: float
    rainfall_forecast: float
    crop_type: str

# ===============================
# ENDPOINTS
# ===============================

@app.get("/health")
def health():
    return {"status": "online", "db_rows": 5223}

@app.get("/data/petrignano")
def get_petrignano(limit: int = 100, db = Depends(get_db)):
    from sqlalchemy import text
    query = text("SELECT * FROM sensor_data LIMIT :limit")
    result = db.execute(query, {"limit": limit})
    return [dict(row._mapping) for row in result]

@app.post("/smart-irrigation")
def smart_irrigation(data: IrrigationInput):
    return {"message": "AI Module (TensorFlow) is currently offline. Database is active."}

@app.delete("/data/cleanup")
def cleanup_old_data(months: int = 6, db: Session = Depends(get_db)):
    """
    Deletes data older than the specified number of months.
    """
    try:
        query = text("DELETE FROM sensor_data WHERE timestamp < date('now', :period)")
        db.execute(query, {"period": f"-{months} months"})
        db.commit()
        return {"message": f"Successfully cleared data older than {months} months."}
    except Exception as e:
        return {"error": str(e)}
    

# Threshold used to detect abnormal flow rate
LEAK_FLOW_RATE_THRESHOLD = 40.0

@app.post("/ingest")
def ingest(data: SensorData, db = Depends(get_db)):
    """
    Receives sensor data, checks for leaks, logs alerts to DB, and sends Discord notifications.
    """
    # 1. Leak Detection Logic
    leak_by_status = (data.status or "").strip().lower() == "leak"
    leak_by_flow = data.flow_rate >= LEAK_FLOW_RATE_THRESHOLD
    leak_detected = leak_by_status or leak_by_flow
    alert_sent = False

    if leak_detected:
        # 2. Prepare Alert Payload
        alert_payload = {
            "device_id": data.device_id,
            "flow_rate": data.flow_rate,
            "water_level": data.water_level,
            "temperature": data.temperature,
            "status": "Leak",
            "timestamp": (data.timestamp or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        }

        # 3. New Step: Log to Database (Requirement)
        try:
            from alert_service import log_alert_to_db
            log_alert_to_db(db, alert_payload)
        except Exception as e:
            print(f"DB Logging Error: {e}")

        # 4. Existing Step: Send Discord Notification
        try:
            alert_sent = send_discord_alert(alert_payload)
        except Exception as e:
            print(f"Discord Alert Error: {e}")

    return {
        "message": "Data received",
        "leak_detected": leak_detected,
        "alert_sent": alert_sent
    }

@app.get("/data/alerts")
def get_all_alerts(db: Session = Depends(get_db)):
    """
    Fetches all logged alerts from the database.
    """
    try:
        query = text("SELECT * FROM alerts ORDER BY timestamp DESC")
        result = db.execute(query)
        return [dict(row._mapping) for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))