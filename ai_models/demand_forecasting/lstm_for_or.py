"""
LSTM Forecast Module for OR Integration

This module provides a function `forecast_for_or` that predicts the next 24 hours of groundwater depth
using a trained LSTM model and a pre-fitted scaler.

Key updates in this version:
1. Fixed H5 model loading: `compile=False` avoids errors with Keras metrics during load.
2. Rolling window fixed: ensured shapes are compatible for NumPy concatenation and updates.
3. Model and scaler paths updated to point to the root-level `models/` folder.
4. Fully ready to integrate with Operations Research (OR) modules.

Usage:
    from lstm_for_or import forecast_for_or
    forecast = forecast_for_or(steps=24)
    print(forecast)

This helps partners understand:
- Which problems were fixed.
- How to use the function.
- That the module now produces consistent forecasts for OR integration.
"""

import numpy as np
import pandas as pd
from datetime import timedelta
from tensorflow.keras.models import load_model
import joblib
import os

# -------------------------------
# Automatic base directory
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "Aquifer_Petrignano.csv")

# Models are in the root-level 'models/' folder
MODEL_PATH = os.path.join(BASE_DIR, "models", "water_forecast_model.h5")
SCALER_PATH = os.path.join(BASE_DIR, "models", "scaler.pkl")

# --------------------------------------------------
# Forecast Function for OR
# --------------------------------------------------
def forecast_for_or(
    steps=24,
    target_column="Depth_to_Groundwater_P24",
    temp_column="Temperature_Petrignano"
):

    # Load trained model and scaler
    model = load_model(MODEL_PATH, compile=False)  # compile=False fixes H5 load issue
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

        # --- FIXED SHAPE ISSUE ---
        last_features = last_sequence[-1, 1:].reshape(1, -1)          # shape (1, n-1)
        next_pred_scaled_2d = np.array([[next_pred_scaled]])          # shape (1,1)
        next_full_scaled = np.concatenate([next_pred_scaled_2d, last_features], axis=1)

        # inverse scaling
        next_pred = scaler.inverse_transform(next_full_scaled)[0][0]
        predictions.append(next_pred)

        # update rolling window (FIXED)
        next_row_scaled = np.hstack([next_pred_scaled_2d, last_sequence[-1, 1:].reshape(1, -1)])
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