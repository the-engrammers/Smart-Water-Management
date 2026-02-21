"""
Water Demand Forecasting - LSTM Model

This module contains a function to train a water demand
forecasting model using historical data.

The model uses the last 12 hours to predict
the next hour's water flow rate.
"""

import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import joblib


def train_model(data_path):
    """
    Train LSTM model using cleaned dataset.

    Parameters:
        data_path (str): path to CSV file

    Returns:
        model: trained keras model
    """

    # Load dataset
    df = pd.read_csv(data_path)

    # Convert timestamp column
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Create time features
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek

    # Select relevant columns
    features = ["flow_rate", "temperature", "hour", "day_of_week"]

    # Scale data between 0 and 1
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[features])

    # Save scaler for later use
    joblib.dump(scaler, "scaler.pkl")

    # Create sequences (12-hour window)
    X = []
    y = []
    window_size = 12

    for i in range(len(scaled) - window_size):
        X.append(scaled[i:i + window_size])
        y.append(scaled[i + window_size][0])

    X = np.array(X)
    y = np.array(y)

    # Build model
    model = Sequential()
    model.add(LSTM(64, input_shape=(window_size, len(features))))
    model.add(Dense(32, activation="relu"))
    model.add(Dense(1))

    model.compile(optimizer="adam", loss="mse")

    # Train model
    model.fit(X, y, epochs=20, batch_size=32)

    # Save trained model
    model.save("model.h5")

    print("Training complete. Model saved as model.h5")

    return model


if __name__ == "__main__":
    print("This script expects a cleaned dataset.")
    print("Call train_model('your_cleaned_data.csv') to train.")