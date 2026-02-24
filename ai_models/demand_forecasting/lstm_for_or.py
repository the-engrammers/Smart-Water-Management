# lstm_for_or.py
# --------------------------------------------------
# LSTM Forecast Module for OR Integration
# --------------------------------------------------

import numpy as np
import pandas as pd
from datetime import timedelta
from tensorflow.keras.models import load_model
import joblib
import os

# -------------------------------
# Automatic base directory
# -------------------------------
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

DATA_PATH = os.path.join(BASE_DIR, "data", "Aquifer_Petrignano.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "water_forecast_model.h5")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "models", "scaler.pkl")


# --------------------------------------------------
# Forecast Function for OR
# --------------------------------------------------
def forecast_for_or(
    steps=24,
    target_column="Depth_to_Groundwater_P24",
    temp_column="Temperature_Petrignano"
):

    # Load trained model and scaler
    model = load_model(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    # Load data
    df = pd.read_csv(DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    df["hour"] = 0
    df["day_of_week"] = df["Date"].dt.dayofweek

    features = [target_column, temp_column, "hour", "day_of_week"]
    df[features] = df[features].ffill()

    scaled_data = scaler.transform(df[features])

    # Prepare last 12 steps
    window_size = 12
    last_sequence = scaled_data[-window_size:]
    predictions = []

    for _ in range(steps):
        input_seq = np.expand_dims(last_sequence, axis=0)
        next_pred_scaled = model.predict(input_seq, verbose=0)[0][0]

        # prepare full row for inverse scaling
        last_features = last_sequence[-1, 1:].reshape(1, -1)
        next_full_scaled = np.concatenate([[next_pred_scaled], last_features], axis=1)

        # inverse scaling
        next_pred = scaler.inverse_transform(next_full_scaled)[0][0]
        predictions.append(next_pred)

        # update rolling window
        next_row_scaled = np.array([next_pred_scaled] + list(last_sequence[-1, 1:]))
        last_sequence = np.vstack([last_sequence[1:], next_row_scaled])

    # Build OR-ready DataFrame
    last_date = df["Date"].iloc[-1]

    forecast_df = pd.DataFrame({
        "Timestamp": [last_date + timedelta(hours=i+1) for i in range(steps)],
        "Predicted_Depth": predictions
    })

    return forecast_df


# --------------------------------------------------
# Run test
# --------------------------------------------------
if __name__ == "__main__":
    forecast = forecast_for_or(steps=24)
    print("\n📊 24-Hour Forecast for OR Model:\n")
    print(forecast)