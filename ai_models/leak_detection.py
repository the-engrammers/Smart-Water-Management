import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATA_PATH = PROJECT_ROOT / "data" / "Aquifer_Petrignano.csv"
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


def load_training_data(data_path: Path = DATA_PATH) -> pd.DataFrame:
    data = pd.read_csv(data_path)

    for column in FEATURES:
        if column not in data.columns:
            raise ValueError(f"Missing required column: {column}")

    model_data = data[FEATURES].dropna().copy()
    return model_data


def train_and_save_model(data_path: Path = DATA_PATH):
    data = load_training_data(data_path)

    threshold = data["Volume_C10_Petrignano"].quantile(0.95)
    data["Leakage_Flag"] = np.where(data["Volume_C10_Petrignano"] > threshold, 1, 0)

    X = data[FEATURES]
    y = data["Leakage_Flag"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42,
    )

    model.fit(X_train[y_train == 0])

    y_pred = model.predict(X_test)
    y_pred = np.where(y_pred == -1, 1, 0)

    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)
    print(classification_report(y_test, y_pred))

    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"Model saved to {MODEL_PATH}")
    print(f"Scaler saved to {SCALER_PATH}")

    return model, scaler


def predict_leak(json_input: str):
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    data_dict = json.loads(json_input)
    input_data = np.array([[data_dict[feature] for feature in FEATURES]])

    input_scaled = scaler.transform(input_data)
    score = model.decision_function(input_scaled)[0]
    leak_probability = 1 / (1 + np.exp(score))

    prediction = model.predict(input_scaled)[0]
    leak_flag = "Leak" if prediction == -1 else "No Leak"

    return {
        "leak_probability": float(leak_probability),
        "prediction": leak_flag,
    }


if __name__ == "__main__":
    train_and_save_model()

    sample_json = json.dumps(
        {
            "Rainfall_Bastia_Umbra": 10,
            "Depth_to_Groundwater_P24": -20,
            "Depth_to_Groundwater_P25": -18,
            "Temperature_Bastia_Umbra": 15,
            "Temperature_Petrignano": 16,
            "Volume_C10_Petrignano": 150000,
            "Hydrometry_Fiume_Chiascio_Petrignano": 3,
        }
    )

    result = predict_leak(sample_json)
    print(result)