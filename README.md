# 💧 Smart Water Management

## 📌 Project Overview

Smart Water Management is an IoT-based real-time monitoring system designed to detect abnormal water flow rates, simulate leak detection, trigger automated alerts, and provide a live dashboard for monitoring and decision support.

---

## 🏗️ System Architecture

Simulator → FastAPI Backend → Alert Service → Streamlit Dashboard

---

## 🚀 Core Features

- Real-time sensor data ingestion  
- Strict input validation (Pydantic)  
- Leak detection threshold logic  
- Discord alert integration  
- Structured logging system  
- Interactive monitoring dashboard  
- Modular architecture for scalability  

---

## 🛠 Technology Stack

- FastAPI (Backend API)  
- Pydantic (Validation)  
- Uvicorn (ASGI Server)  
- Streamlit (Dashboard)  
- Pandas (Data Handling)  
- Requests (Alert Service)  
- Python Logging Module  

---

## ▶️ How to Run (Full Stack)

### 🔹 Backend

bash
uvicorn backend.main:app --reload
🔹 Dashboard
cd frontend
streamlit run app.py
🔹 Alert Simulation
python backend/alert_service.py
📡 API Endpoint
POST /ingest
Expected JSON
{
  "device_id": "sensor_01",
  "flow_rate": 25.5,
  "timestamp": "2026-02-25T14:30:00"
}
Validation Rules

device_id: required, non-empty

flow_rate: must be > 0

timestamp: optional

✅ Phase 1 Status: Monitoring

The live monitoring stack is now integrated and ready for team use:

Streamlit dashboard for live leak visibility (frontend/app.py)

Alert simulation service with CSV logging (backend/alert_service.py)

Project hygiene via .gitignore to exclude runtime/cache files

🖥 Demo Run Commands
# Terminal 1
cd frontend
streamlit run app.py

# Terminal 2
cd ..
python backend/alert_service.py
🚧 Phase 2 Assignments
👤 Member 5 — Decision Support UI & Farmer Controls

Add Smart Action Box showing AI decision and reason

Add START/STOP PUMP controls on dashboard

Add Water Saved optimization metric/chart vs traditional irrigation

👤 Member 7 — Intelligence Logic (Rules Engine)

Build irrigation decision logic based on Operations Research rules

Expose decision variables for Member 5 UI integration

Provide decision payload (action, reason, confidence/timing)

📸 Dashboard Evidence (Monitoring Phase)

Add the latest dashboard screenshot here after each validated demo run.

Suggested path:

docs/images/monitoring-phase-dashboard.png
🏁 Conclusion

This project demonstrates a complete real-time monitoring pipeline integrating backend validation, automated alerting, structured logging, and interactive visualization within a modular and scalable architecture.
