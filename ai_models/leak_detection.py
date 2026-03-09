import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "leak_detection_model.pkl"
SCALER_PATH = BASE_DIR / "leak_scaler.pkl"

FEATURES = [
    "Rainfall_Bastia_Umbra",
    "Depth_to_Groundwater_P24",
    "Depth_to_Groundwater_P25",
    "Temperature_Bastia_Umbra",
    "Temperature_Petrignano",
    "Volume_C10_Petrignano",
    "Hydrometry_Fiume_Chiascio_Petrignano",
]


class LeakDetectionModel:

    def __init__(self):
        # charger une seule fois
        self.model = joblib.load(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)

    def predict(self, data_dict):

        input_data = np.array([[data_dict[f] for f in FEATURES]])

        input_scaled = self.scaler.transform(input_data)

        score = self.model.decision_function(input_scaled)[0]

        leak_probability = 1 / (1 + np.exp(score))

        prediction = self.model.predict(input_scaled)[0]

        leak_flag = "Leak" if prediction == -1 else "No Leak"

        return {
            "leak_probability": float(leak_probability),
            "prediction": leak_flag,
        }
