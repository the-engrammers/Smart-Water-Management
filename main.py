from ai_models.leak_detection import predict_leak

@app.post("/predict/leak")
def leak_prediction(sensor_data: list):

    try:
        result = predict_leak(leak_model, sensor_data)
        return result

    except Exception:
        # fallback logique seuil
        if sensor_data[0] > 100:
            return {"leak": True, "method": "threshold"}
        else:
            return {"leak": False, "method": "threshold"}
