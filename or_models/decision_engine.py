from .irrigation_optimizer import optimize_irrigation
from .pump_scheduler import schedule_pump


def make_decision(predicted_water_need):

    irrigation = optimize_irrigation(predicted_water_need, 100)

    pump_time = schedule_pump(irrigation, 0.2)

    decision = {
        "action": "start_irrigation",
        "reason": "predicted demand requires irrigation",
        "confidence": 0.85,
        "timing": "next_hour",
        "water_amount": irrigation,
        "pump_hours": pump_time
    }

    return decision