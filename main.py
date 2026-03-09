from fastapi import FastAPI
import joblib

from ai_models.leak_detection import predict_leak
from ai_models.demand_forecasting.train_model import predict_demand

app = FastAPI()

leak_model = None
leak_scaler = None
demand_model = None


@app.on_event("startup")
def load_models():
    global leak_model, leak_scaler, demand_model

    # charger modèle fuite
    leak_model = joblib.load("ai_models/leak_detection_model.pkl")
    leak_scaler = joblib.load("ai_models/leak_scaler.pkl")

    # charger modèle LSTM
    from tensorflow.keras.models import load_model
    demand_model = load_model("ai_models/demand_model.h5")

    print("Models loaded successfully")


# -----------------------
# LEAK DETECTION API
# -----------------------
@app.post("/predict/leak")
def leak_prediction(sensor_data: dict):

    try:
        result = predict_leak(sensor_data, leak_model, leak_scaler)
        return result

    except Exception:

        # fallback logique seuil
        volume = sensor_data.get("Volume_C10_Petrignano", 0)

        if volume > 150000:
            return {"prediction": "Leak", "method": "threshold"}
        else:
            return {"prediction": "No Leak", "method": "threshold"}


# -----------------------
# DEMAND FORECAST API
# -----------------------
@app.post("/predict/demand")
def demand_prediction(data: list):

    result = predict_demand(demand_model, data)

    return result
