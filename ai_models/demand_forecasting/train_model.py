"""
Water Demand Forecasting - Phase 2

This script trains an LSTM model to predict the next
24 hours of water demand using the previous 24 hours.

The predicted demand is saved in a CSV file so that
the OR model can use it as a daily requirement.
"""

import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import joblib



# Train the model


def train_model(data_path):

    # Load dataset
    df = pd.read_csv(data_path)

    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Extract time features
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek

    # Features used for training
    features = ["flow_rate", "temperature", "water_level", "hour", "day_of_week"]

    # Scale the data
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df[features])

    # Save scaler
    joblib.dump(scaler, "scaler.pkl")

    # Create sequences
    window_size = 24        # use past 24 hours
    forecast_horizon = 24   # predict next 24 hours

    X = []
    y = []

    for i in range(len(scaled_data) - window_size - forecast_horizon):
        X.append(scaled_data[i:i+window_size])
        y.append(scaled_data[i+window_size:i+window_size+forecast_horizon, 0])

    X = np.array(X)
    y = np.array(y)

    # Build LSTM model
    model = Sequential()
    model.add(LSTM(64, input_shape=(window_size, len(features))))
    model.add(Dense(32, activation="relu"))
    model.add(Dense(forecast_horizon))  # 24 outputs

    model.compile(optimizer="adam", loss="mse")

    # Train model
    model.fit(X, y, epochs=25, batch_size=32)

    # Save model
    model.save("lstm_model_24h.h5")

    print("Model training finished and saved successfully.")

    return model


# Make 24-hour prediction for OR


def predict_next_24_hours(data_path):

    # Load model and scaler
    model = load_model("lstm_model_24h.h5")
    scaler = joblib.load("scaler.pkl")

    df = pd.read_csv(data_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek

    features = ["flow_rate", "temperature", "water_level", "hour", "day_of_week"]

    scaled_data = scaler.transform(df[features])

    window_size = 24

    # Take last 24 hours as input
    last_window = scaled_data[-window_size:]
    last_window = np.expand_dims(last_window, axis=0)

    # Predict
    prediction_scaled = model.predict(last_window)

    # Reverse scaling only for flow_rate
    temp_array = np.zeros((24, len(features)))
    temp_array[:, 0] = prediction_scaled[0]

    prediction = scaler.inverse_transform(temp_array)
    predicted_flow = prediction[:, 0]

    # Save results for OR model
    demand_df = pd.DataFrame({
        "hour": range(1, 25),
        "predicted_flow_rate": predicted_flow
    })

    demand_df.to_csv("daily_demand.csv", index=False)

    print("24-hour demand saved to daily_demand.csv")

    return predicted_flow


# Main


if __name__ == "__main__":
    print("Run train_model('cleaned_data.csv') to train the model.")
    print("Run predict_next_24_hours('cleaned_data.csv') to generate forecast.")