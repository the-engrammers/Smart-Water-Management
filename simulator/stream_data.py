import pandas as pd
import requests
import time
import random
import numpy as np
import os
from pathlib import Path

# Updated API_URL to match FastAPI port
API_URL = os.getenv("API_URL", "http://localhost:8000/ingest")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "Aquifer_Petrignano.csv"

def start_sensor():
    print(" Updated Virtual Sensor Started...")
    
    try:
        df = pd.read_csv(CSV_PATH)
        
        for index, row in df.iterrows():
            
            # Extracting values and handling empty (NaN) cells
            flow = row['Volume_C10_Petrignano'] if not pd.isna(row['Volume_C10_Petrignano']) else 0
            # Renaming 'pressure' to 'water_level' as requested
            level = row['Depth_to_Groundwater_P24'] if not pd.isna(row['Depth_to_Groundwater_P24']) else 0
            # Adding Temperature column
            temp = row['Temperature_Petrignano'] if not pd.isna(row['Temperature_Petrignano']) else 20.0

            # Updated JSON Format
            payload = {
                "device_id": "Zone_A_01", # Renamed from sensor_id
                "flow_rate": abs(float(flow)), 
                "water_level": abs(float(level)), # Renamed from pressure
                "temperature": float(temp), # New field
                "status": "Leak" if abs(float(flow)) >= 40 else "Normal",
                "timestamp": pd.Timestamp.now().isoformat()
            }

            try:
                response = requests.post(API_URL, json=payload) 
                print(f"Data sent: Row {index} | Status: {response.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"Connection Error: Backend (FastAPI) at {API_URL} not found.") 

            time.sleep(random.randint(5, 10))

    except FileNotFoundError:
        print(f" Error: Could not find {CSV_PATH}")

if __name__ == "__main__":
    start_sensor()