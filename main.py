from fastapi import FastAPI
import numpy as np

from ai_models.leak_detection import LeakDetector
from ai_models.demand_forecasting.train_model import predict_demand

app = FastAPI()

# Instantiate models once at startup
leak_detector = None
demand_model = None


@app.on_event("startup")
def load_models():
    global leak_detector, demand_model

    # Load class-based leak detector (loads model + scaler internally)
    leak_detector = LeakDetector()

    # Load LSTM demand model
    from tensorflow.keras.models import load_model
    demand_model = load_model("ai_models/demand_model.h5")

    print("Models loaded successfully")


# -----------------------
# LEAK DETECTION API
# -----------------------
@app.post("/predict/leak")
def leak_prediction(sensor_data: dict):
    """
    Expects a JSON body with sensor feature keys.
    Uses the class-based LeakDetector which handles ML + fallback internally.
    """
    result = leak_detector.predict(sensor_data)
    return result


# -----------------------
# DEMAND FORECAST API
# -----------------------
@app.post("/predict/demand")
def demand_prediction(data: list):
    """
    Expects a list of historical demand values.
    Returns the predicted next-hour demand.
    """
    result = predict_demand(demand_model, data)
    return result
