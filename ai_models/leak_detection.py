import json
import joblib
import numpy as np
from pathlib import Path

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


class LeakDetector:

    def __init__(self):
        """Load model and scaler once"""
        self.model = joblib.load(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)

    def predict(self, data_dict):
        """
        data_dict = JSON avec les features
        """

        try:

            input_data = np.array([[data_dict[f] for f in FEATURES]])

            input_scaled = self.scaler.transform(input_data)

            score = self.model.decision_function(input_scaled)[0]
            leak_probability = 1 / (1 + np.exp(score))

            prediction = self.model.predict(input_scaled)[0]

            leak_flag = prediction == -1

            return {
                "leak": bool(leak_flag),
                "probability": float(leak_probability),
                "source": "ml_model"
            }

        except Exception as e:

            # fallback simple
            if data_dict["Volume_C10_Petrignano"] > 150000:
                return {
                    "leak": True,
                    "source": "threshold_fallback"
                }

            return {
                "leak": False,
                "source": "threshold_fallback"
            }
