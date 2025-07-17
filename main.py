import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

INTERVALS_API_TOKEN = os.getenv("INTERVALS_API_TOKEN")
ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID")
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY")
LAST_CHECK_FILE = "last_check.txt"


def get_recent_activities():
    url = "https://intervals.icu/api/v1/athlete/activities"
    headers = {
        "Authorization": f"Bearer {INTERVALS_API_TOKEN}"
    }
    params = {
        "limit": 5
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def get_activity_details(activity_id):
    url = f"https://intervals.icu/api/v1/activities/{activity_id}"
    headers = {
        "Authorization": f"Bearer {INTERVALS_API_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_last_check_time():
    try:
        with open(LAST_CHECK_FILE, "r") as f:
            return datetime.fromisoformat(f.read().strip())
    except:
        return datetime.utcnow() - timedelta(minutes=10)


def save_last_check_time(t):
    with open(LAST_CHECK_FILE, "w") as f:
        f.write(t.isoformat())


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


def check_new_comments(activity):
    details = get_activity_details(activity["id"])
    comments = details.get("comments", [])
    last_check = get_last_check_time()

    for comment in comments:
        comment_time = datetime.fromisoformat(comment["date"])
        if comment_time > last_check:
            send_push_notification("Nowy komentarz", f'{comment["authorName"]}: {comment["comment"]}')


def main():
    print("Sprawdzanie aktywności...")
    last_check = get_last_check_time()
    activities = get_recent_activities()

    for act in activities:
        start_date = datetime.fromisoformat(act["date"])
        if start_date > last_check:
            send_push_notification(
                "Nowy trening!",
                f'{act["description"] or "Brak opisu"} - {act["sportType"]}'
            )
        check_new_comments(act)

    save_last_check_time(datetime.utcnow())


if __name__ == "__main__":
    main()
