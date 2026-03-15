import csv
import os
from datetime import datetime
from pathlib import Path
import requests
import time
from backend.notifications.notification_manager import NotificationManager
from backend.notifications.severity import Severity
from backend.notifications.alert_status import AlertStatus
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

# ===============================
# SECURITY: Load secret from ENV
# ===============================

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

ROOT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = ROOT_DIR / "frontend" / "alert_logs.csv"


CSV_FIELDS = [
    'timestamp',
    'device_id',
    'flow_rate',
    'water_level',
    'temperature',
    'status'
]

# ===============================
# Notification System Variables
# ===============================
user_prefs = {}  # Example: {user_id: {"sms": "+1234567890", "email": "user@example.com"}}
notification_manager = NotificationManager(user_prefs)
alert_cooldowns = {}  # {(user_id, alert_type): last_sent_time}
alert_acknowledgments = {}  # {(user_id, alert_id): status}

# ===============================
# Ensure CSV schema
# ===============================

def ensure_log_schema() -> None:
    if not os.path.isfile(LOG_FILE):
        return


def send_alert(user_id, alert_type, message, subject, severity=Severity.INFO, cooldown=300):
    now = time.time()
    cooldown_key = (user_id, alert_type)
    if cooldown_key in alert_cooldowns and now - alert_cooldowns[cooldown_key] < cooldown:
        return 'Cooldown active, alert not sent.'
    result = notification_manager.send_alert(user_id, message, subject, severity)
    alert_cooldowns[cooldown_key] = now
    # Track alert status
    alert_id = f"{user_id}_{alert_type}_{int(now)}"
    alert_acknowledgments[(user_id, alert_id)] = AlertStatus.UNSEEN
    return result

def acknowledge_alert(user_id, alert_id, status=AlertStatus.SEEN):

    if (user_id, alert_id) in alert_acknowledgments:
        alert_acknowledgments[(user_id, alert_id)] = status
        return True
    return False


# ===============================
# Log alerts to CSV
# ===============================

def log_alert_to_csv(data):

    file_exists = os.path.isfile(LOG_FILE)

    Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

    ensure_log_schema()

    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as file_handle:

        writer = csv.DictWriter(file_handle, fieldnames=CSV_FIELDS)

        if not file_exists:
            writer.writeheader()

        writer.writerow(
            {
                "timestamp": data["timestamp"],
                "device_id": data["device_id"],
                "flow_rate": data["flow_rate"],
                "water_level": data.get("water_level", ""),
                "temperature": data.get("temperature", ""),
                "status": data["status"],
            }
        )

    print(f"Alert logged successfully to {LOG_FILE}")


# ===============================
# Send Discord Alert
# ===============================

def send_discord_alert(data):

    if not DISCORD_WEBHOOK_URL:
        print("⚠ DISCORD_WEBHOOK_URL not configured.")
        log_alert_to_csv(data)
        return False

    payload = {
        "username": "Water Guard Bot",
        "embeds": [
            {
                "title": "🚨 CRITICAL ALERT: LEAK DETECTED 🚨",
                "color": 16711680,
                "fields": [
                    {"name": "Device ID", "value": data["device_id"], "inline": True},
                    {"name": "Flow Rate", "value": f"{data['flow_rate']} L/min", "inline": True},
                    {"name": "Water Level", "value": f"{data.get('water_level','N/A')} m", "inline": True},
                    {"name": "Temperature", "value": f"{data.get('temperature','N/A')} °C", "inline": True},
                    {"name": "Timestamp", "value": data["timestamp"], "inline": False},
                ],
            }
        ],
    }

    try:

        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)

        if response.status_code == 204:
            print("✅ Alert sent to Discord")
            log_alert_to_csv(data)
            return True

        print(f"❌ Failed to send alert. Status: {response.status_code}")
        log_alert_to_csv(data)
        return False

    except Exception as error:

        print(f"Error sending alert: {error}")
        log_alert_to_csv(data)
        return False


# ===============================
# Test
# ===============================

if __name__ == "__main__":

    test_data = {
        "device_id": "SN-MEKNES-001",
        "flow_rate": 45.2,
        "water_level": 2.8,
        "temperature": 23.5,
        "status": "Leak",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    if test_data["status"] == "Leak":
        send_discord_alert(test_data)


def log_alert_to_db(db: Session, alert_data: dict):
    """
    Logs the alert details into the SQL database alerts table.
    """
    try:
        query = text("""
            INSERT INTO alerts (device_id, alert_type, message, timestamp) 
            VALUES (:device_id, :type, :msg, :timestamp)
        """)
        db.execute(query, {
            "device_id": alert_data["device_id"],
            "type": "Leak Detection",
            "msg": f"High flow rate detected: {alert_data['flow_rate']}",
            "timestamp": alert_data["timestamp"]
        })
        db.commit()
    except Exception as e:
        print(f"Failed to log alert to DB: {e}")