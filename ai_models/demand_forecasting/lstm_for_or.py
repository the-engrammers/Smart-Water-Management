# lstm_for_or.py
# -------------------------------
# LSTM Forecasting for OR Integration
# -------------------------------

import numpy as np
import pandas as pd
from datetime import timedelta
from tensorflow.keras.models import load_model
import joblib

# -------------------------------
# Multi-step forecast function
# -------------------------------
def forecast_for_or(
    model_path="models/water_forecast_model.h5",
    scaler_path="models/scaler.pkl",
    scaled_data=None,
    start_time=None,
    steps=24
):
    """
    Generates multi-step LSTM forecasts for OR models.

    Parameters:
        model_path (str): Path to trained LSTM model (.h5)
        scaler_path (str): Path to fitted scaler (.pkl)
        scaled_data (np.array): Scaled historical data (last 12 steps used)
        start_time (pd.Timestamp): Start time for forecast timestamps
        steps (int): Number of future steps to predict

    Returns:
        pd.DataFrame: Timestamped predictions for OR input
    """
    # Load model and scaler
    model = load_model(model_path)
    scaler = joblib.load(scaler_path)

    last_sequence = scaled_data[-12:]
    predictions = []

    for _ in range(steps):
        input_seq = np.expand_dims(last_sequence, axis=0)
        next_pred_scaled = model.predict(input_seq, verbose=0)[0][0]

        # Build full row for inverse transform
        last_features = last_sequence[-1, 1:].reshape(1, -1)
        next_pred_scaled_full = np.concatenate([[next_pred_scaled], last_features], axis=1)

        # Inverse scale
        next_pred = scaler.inverse_transform(next_pred_scaled_full)[0][0]
        predictions.append(next_pred)

        # Update last_sequence
        next_row = np.array([next_pred] + list(last_sequence[-1, 1:]))
        last_sequence = np.vstack([last_sequence[1:], next_row])

    # Create DataFrame with timestamps
    if start_time is None:
        start_time = pd.Timestamp.now()
    forecast_df = pd.DataFrame({
        "Timestamp": [start_time + timedelta(hours=i+1) for i in range(steps)],
        "Predicted_Depth": predictions
    })
    return forecast_df


# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    from water_demand_lstm import load_and_preprocess

    # Load & preprocess historical data
    df, scaled_data, scaler, features = load_and_preprocess(
        data_path="data/Aquifer_Petrignano.csv",
        target_column="Depth_to_Groundwater_P24",
        temp_column="Temperature_Petrignano"
    )

    # Forecast next 24 hours
    forecast_df = forecast_for_or(scaled_data=scaled_data, steps=24)
    print(forecast_df)