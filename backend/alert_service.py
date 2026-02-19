import requests
import csv
import os
from datetime import datetime

# --- CONFIGURATION ---
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
LOG_FILE = "alert_logs.csv"

# --- LOGGING FUNCTION ---
def log_alert_to_csv(data):
    """
    Saves the alert details into a CSV file for history tracking.
    """
    file_exists = os.path.isfile(LOG_FILE)

    # Open file in append mode
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["timestamp", "device_id", "flow_rate", "status"])

        # Write header only if the file is new
        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": data["timestamp"],
            "device_id": data["device_id"],
            "flow_rate": data["flow_rate"],
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
        return False

    payload = {
        "username": "Water Guard Bot",
        "embeds": [{
            "title": "🚨 CRITICAL ALERT: LEAK DETECTED 🚨",
            "color": 16711680,
            "fields": [
                {"name": "Device ID", "value": data["device_id"], "inline": True},
                {"name": "Flow Rate", "value": f"{data['flow_rate']} L/min", "inline": True},
                {"name": "Timestamp", "value": data["timestamp"], "inline": False}
            ]
        }]
    }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("Alert sent to Discord!")
            # Once sent to discord, log it for history
            log_alert_to_csv(data)
            return True
        else:
            print(f"Failed to send alert. Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# --- EXECUTION ---
if __name__ == "__main__":
    # Test data
    test_data = {
        "device_id": "SN-MEKNES-001",
        "flow_rate": 45.2,
        "status": "Leak",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if test_data["status"] == "Leak":
        send_discord_alert(test_data)