import requests
import csv
import os
from datetime import datetime
from pathlib import Path

# --- CONFIGURATION ---
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "https://discordapp.com/api/webhooks/1474427883173707938/mChuz3klUQpeh869O_BVNdxaXn5BIYxxymPtdWARYe8bOY0rwiuaj8WAbBPs-dpd6oRZ")
ROOT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = ROOT_DIR / "frontend" / "alert_logs.csv"
CSV_FIELDS = ["timestamp", "device_id", "flow_rate", "water_level", "temperature", "status"]


def ensure_log_schema() -> None:
    if not os.path.isfile(LOG_FILE):
        return

    with open(LOG_FILE, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        current_fields = reader.fieldnames or []

        if current_fields == CSV_FIELDS:
            return

        rows = list(reader)

    with open(LOG_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "timestamp": row.get("timestamp", ""),
                "device_id": row.get("device_id", ""),
                "flow_rate": row.get("flow_rate", ""),
                "water_level": row.get("water_level", ""),
                "temperature": row.get("temperature", ""),
                "status": row.get("status", "")
            })

# --- LOGGING FUNCTION ---
def log_alert_to_csv(data):
    """
    Saves the alert details into a CSV file for history tracking.
    """
    file_exists = os.path.isfile(LOG_FILE)
    Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
    ensure_log_schema()

    # Open file in append mode
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)

        # Write header only if the file is new
        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": data["timestamp"],
            "device_id": data["device_id"],
            "flow_rate": data["flow_rate"],
            "water_level": data.get("water_level", ""),
            "temperature": data.get("temperature", ""),
            "status": data["status"]
        })
    print(f"Alert logged successfully to {LOG_FILE}")

# --- DISCORD ALERT FUNCTION ---
def send_discord_alert(data):
    """
    Sends a formatted alert message to Discord.
    """
    if not DISCORD_WEBHOOK_URL:
        print("DISCORD_WEBHOOK_URL is not set. Alert not sent.")
        log_alert_to_csv(data)
        return False

    payload = {
        "username": "Water Guard Bot",
        "embeds": [{
            "title": "🚨 CRITICAL ALERT: LEAK DETECTED 🚨",
            "color": 16711680,
            "fields": [
                {"name": "Device ID", "value": data["device_id"], "inline": True},
                {"name": "Flow Rate", "value": f"{data['flow_rate']} L/min", "inline": True},
                {"name": "Water Level", "value": f"{data.get('water_level', 'N/A')} m", "inline": True},
                {"name": "Temperature", "value": f"{data.get('temperature', 'N/A')} °C", "inline": True},
                {"name": "Timestamp", "value": data["timestamp"], "inline": False}
            ]
        }]
    }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("Alert sent to Discord!")
            log_alert_to_csv(data)
            return True
        else:
            print(f"Failed to send alert. Status: {response.status_code}")
            log_alert_to_csv(data)
            return False
    except Exception as e:
        print(f"Error: {e}")
        log_alert_to_csv(data)
        return False

# --- EXECUTION ---
if __name__ == "__main__":
    # Test data
    test_data = {
        "device_id": "SN-MEKNES-001",
        "flow_rate": 45.2,
        "water_level": 2.8,
        "temperature": 23.5,
        "status": "Leak",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if test_data["status"] == "Leak":
        send_discord_alert(test_data)