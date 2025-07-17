import os
import requests
from datetime import datetime, timedelta

INTERVALS_API_TOKEN = os.getenv("INTERVALS_API_TOKEN")
ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID")
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY")


def get_recent_activities():
    url = "https://intervals.icu/api/v1/athlete/activities"
    headers = {"Authorization": f"Bearer {INTERVALS_API_TOKEN}"}
    params = {"limit": 5}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def send_push_notification(title, message):
    url = "https://onesignal.com/api/v1/notifications"
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "included_segments": ["All"],
        "headings": {"en": title},
        "contents": {"en": message},
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}",
    }
    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()


def main():
    print("Sprawdzanie aktywności...")
    activities = get_recent_activities()
    now = datetime.utcnow()
    for act in activities:
        act_time = datetime.fromisoformat(act["date"])
        if now - act_time < timedelta(minutes=10):
            send_push_notification(
                "Nowy trening!",
                f"{act['description'] or 'Brak opisu'} - {act['sportType']}"
            )


if __name__ == "__main__":
    main()
