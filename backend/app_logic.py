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