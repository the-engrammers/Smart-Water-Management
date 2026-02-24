import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import joblib
import os
import matplotlib.pyplot as plt

# -------------------------------
# Automatic relative data path
# -------------------------------
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

DATA_PATH = os.path.join(BASE_DIR, "data", "Aquifer_Petrignano.csv")

# -------------------------------
# Helper function to create sequences
# -------------------------------
def create_sequences(data, window_size=12):
    X, y = [], []
    for i in range(len(data) - window_size):
        X.append(data[i:i+window_size])
        y.append(data[i+window_size][0])
    return np.array(X), np.array(y)

# -------------------------------
# Main training function
# -------------------------------
def train_lstm_model(
    data_path=DATA_PATH,
    model_dir="models",
    epochs=20,
    batch_size=32,
    target_column="Depth_to_Groundwater_P24",
    temp_column="Temperature_Petrignano"
):
    # Load data
    df = pd.read_csv(data_path)

    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    df["hour"] = 0
    df["day_of_week"] = df["Date"].dt.dayofweek

    features = [target_column, temp_column, "hour", "day_of_week"]
    df[features] = df[features].ffill()

    # Scale features
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df[features])

    # Save scaler
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(scaler, os.path.join(model_dir, "scaler.pkl"))

    # Create sequences
    X, y = create_sequences(scaled_data, window_size=12)

    # Build LSTM
    model = Sequential()
    model.add(LSTM(64, input_shape=(X.shape[1], X.shape[2])))
    model.add(Dense(32, activation="relu"))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mse")

    # Train
    history = model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)

    # Save model
    model.save(os.path.join(model_dir, "water_forecast_model.h5"))

    # -------------------------------
    # Plot training loss
    # -------------------------------
    plt.figure(figsize=(8,4))
    plt.plot(history.history['loss'], label='Training Loss')
    plt.title('LSTM Training Loss')
    plt.xlabel('Epoch')
    plt.ylabel('MSE')
    plt.legend()
    plt.show()

    # -------------------------------
    # Plot predictions vs true values
    # -------------------------------
    y_pred = model.predict(X)

    plt.figure(figsize=(12,4))
    plt.plot(y[:100], label='True')
    plt.plot(y_pred[:100], label='Predicted')
    plt.title('Groundwater Depth Predictions (First 100 points)')
    plt.xlabel('Time step')
    plt.ylabel('Scaled Depth')
    plt.legend()
    plt.show()

    # -------------------------------
    # Predict next hour groundwater depth
    # -------------------------------
    last_sequence = scaled_data[-12:]
    last_sequence_input = np.expand_dims(last_sequence, axis=0)

    next_pred_scaled = model.predict(last_sequence_input)

    last_features = last_sequence[-1, 1:].reshape(1, -1)

    next_pred_scaled_full = np.concatenate([next_pred_scaled, last_features], axis=1)

    next_pred = scaler.inverse_transform(next_pred_scaled_full)[0][0]

    print(f"✅ Predicted groundwater depth for next hour: {next_pred:.2f}")

    return model, scaler, X, y


# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    train_lstm_model()