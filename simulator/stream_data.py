import pandas as pd
import requests
import time
import random
import numpy as np

# CONFIGURATION
# You will replace this with the real team API URL later
API_URL = "http://localhost:5000/api/water" 
CSV_PATH = "data/Aquifer_Petrignano.csv" 

def start_sensor():
    print(" Virtual Sensor Started using Petrignano Aquifer Data...")
    
    try:
        df = pd.read_csv(CSV_PATH)
        
        # Iterating through rows to simulate real-time data flow
        for index, row in df.iterrows():
            
            # Mapping Petrignano columns to your team's JSON format
            # Volume_C10_Petrignano acts as flow_rate
            # Depth_to_Groundwater_P24 acts as a proxy for pressure
            flow = row['Volume_C10_Petrignano'] if not pd.isna(row['Volume_C10_Petrignano']) else 0
            depth = row['Depth_to_Groundwater_P24'] if not pd.isna(row['Depth_to_Groundwater_P24']) else 0

            payload = {
                "sensor_id": "Zone_A_01",
                "flow_rate": abs(float(flow)), 
                "pressure": abs(float(depth)),
                "timestamp": pd.Timestamp.now().isoformat()
            }

            try:
                # This fulfills the "send a JSON POST request" requirement
                response = requests.post(API_URL, json=payload) 
                print(f"Data sent: Row {index} | Status: {response.status_code}")
            except requests.exceptions.ConnectionError:
                # This fulfills the "handle Connection Error" requirement
                print(f"Connection Error at row {index}: API is offline. Continuing...") 

            # This fulfills the "every 5-10 seconds" requirement
            time.sleep(random.randint(5, 10))

    except FileNotFoundError:
        print(f"Error: Could not find {CSV_PATH}")

if __name__ == "__main__":
    start_sensor()