# backend/decision_engine.py

# We use dataclass to structure incoming sensor data cleanly.
# This keeps the decision engine organized and readable.
from dataclasses import dataclass


@dataclass
class SensorData:
    """
    Represents real-time environmental and crop data
    collected from sensors and external APIs.
    """
    soil_moisture: float        # Current soil moisture percentage (0–100)
    temperature: float          # Ambient temperature in Celsius
    humidity: float             # Air humidity percentage
    rainfall_forecast: float    # Expected rainfall in mm (next 24h)
    crop_type: str              # Crop being irrigated (e.g., wheat, corn)


# Soil moisture threshold (%) required per crop type.
# If soil moisture falls below this value, irrigation is triggered.
CROP_THRESHOLDS = {
    "wheat": 35,
    "corn": 40,
    "rice": 60,
    "default": 30  # Used if crop type is unknown
}


def get_crop_threshold(crop_type: str) -> float:
    """
    Returns the soil moisture threshold for a given crop.
    Falls back to a default value if crop type is not defined.
    """
    return CROP_THRESHOLDS.get(crop_type.lower(), CROP_THRESHOLDS["default"])


def calculate_recommended_duration(deficit: float, temperature: float) -> int:
    """
    Determines irrigation duration based on:
    - Moisture deficit (how far below threshold we are)
    - Temperature (hotter weather requires more water)

    Heuristic model:
    - Base duration = 10 minutes
    - Add 1 minute for every 2% moisture deficit
    - Add 5 extra minutes if temperature > 32°C
    - Clamp duration between 5 and 45 minutes
    """
    base = 10

    # Increase duration proportionally to moisture deficit
    duration = base + int(deficit / 2)

    # Increase watering time in high heat conditions
    if temperature > 32:
        duration += 5

    # Ensure duration stays within reasonable limits
    return max(5, min(duration, 45))


def make_irrigation_decision(sensor: SensorData) -> dict:
    """
    Core decision-making function.

    Applies rule-based logic using:
    - Rain forecast
    - Soil moisture threshold
    - Temperature adjustments

    Returns structured decision payload:
    {
        action: START_IRRIGATION or STOP_IRRIGATION,
        reason: Explanation for decision,
        confidence: Confidence score (0–1),
        recommended_duration: Irrigation time in minutes
    }
    """

    # Get crop-specific soil moisture threshold
    threshold = get_crop_threshold(sensor.crop_type)

    # Rule 1: If significant rain is expected, avoid irrigation
    # Rainfall > 5mm in next 24 hours overrides irrigation
    if sensor.rainfall_forecast > 5:
        return {
            "action": "STOP_IRRIGATION",
            "reason": "Rain forecast exceeds 5mm",
            "confidence": 0.9,
            "recommended_duration": 0
        }

    # Rule 2: If soil moisture is below threshold, start irrigation
    if sensor.soil_moisture < threshold:
        # Calculate how far below optimal level we are
        deficit = threshold - sensor.soil_moisture

        # Estimate irrigation duration
        duration = calculate_recommended_duration(deficit, sensor.temperature)

        # Confidence increases as deficit increases
        confidence = min(0.95, 0.6 + (deficit / 100))

        return {
            "action": "START_IRRIGATION",
            "reason": f"Soil moisture below {threshold}% threshold",
            "confidence": round(confidence, 2),
            "recommended_duration": duration
        }

    # Rule 3: Soil moisture is adequate → no irrigation needed
    return {
        "action": "STOP_IRRIGATION",
        "reason": "Soil moisture within optimal range",
        "confidence": 0.8,
        "recommended_duration": 0
    }