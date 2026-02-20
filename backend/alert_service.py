from __future__ import annotations

import csv
import datetime as dt
import json
from pathlib import Path
import os
import urllib.error
import urllib.request

STATUS = "Leak"
DEVICE_ID = "SN-MEKNES-001"
FLOW_RATE = 7.25
ROOT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = ROOT_DIR / "frontend" / "alert_logs.csv"
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "https://discordapp.com/api/webhooks/1474427883173707938/mChuz3klUQpeh869O_BVNdxaXn5BIYxxymPtdWARYe8bOY0rwiuaj8WAbBPs-dpd6oRZ")


def send_discord_alert(payload: dict) -> None:
    if not DISCORD_WEBHOOK_URL:
        print("[INFO] DISCORD_WEBHOOK_URL not set. Skipping Discord send.")
        return

    message = {
        "content": (
            f"🚨 Leak Alert\n"
            f"Device: {payload['device_id']}\n"
            f"Flow Rate: {payload['flow_rate']} L/min\n"
            f"Timestamp: {payload['timestamp']}"
        )
    }

    request = urllib.request.Request(
        DISCORD_WEBHOOK_URL,
        data=json.dumps(message).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if 200 <= response.status < 300:
                print("[OK] Discord alert sent.")
            else:
                print(f"[WARN] Discord returned status {response.status}.")
    except (urllib.error.URLError, urllib.error.HTTPError) as error:
        print(f"[WARN] Discord send failed: {error}")


def append_to_log(payload: dict) -> None:
    file_exists = LOG_FILE.exists()
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    with LOG_FILE.open("a", newline="", encoding="utf-8") as file_handle:
        writer = csv.DictWriter(
            file_handle,
            fieldnames=["timestamp", "device_id", "flow_rate", "status"],
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(payload)

    print(f"[OK] Logged leak to {LOG_FILE}")


def main() -> None:
    payload = {
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "device_id": DEVICE_ID,
        "flow_rate": FLOW_RATE,
        "status": STATUS,
    }

    if payload["status"] != "Leak":
        print("[INFO] Status is not 'Leak'. No alert/log action taken.")
        return

    send_discord_alert(payload)
    append_to_log(payload)
    print("\a", end="")
    print("[OK] Notification triggered.")


if __name__ == "__main__":
    main()
