import os
import requests

def send_onesignal_push(title, message):
    app_id = os.getenv("ONESIGNAL_APP_ID")
    api_key = os.getenv("ONESIGNAL_API_KEY")
    if not app_id or not api_key:
        print("Brak ONESIGNAL_APP_ID lub ONESIGNAL_API_KEY w zmiennych środowiskowych")
        return False

    url = "https://onesignal.com/api/v1/notifications"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {api_key}"
    }

    payload = {
        "app_id": app_id,
        "included_segments": ["All"],  # lub listę device_ids w "include_player_ids"
        "headings": {"en": title},
        "contents": {"en": message}
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Powiadomienie push wysłane!")
        return True
    else:
        print(f"Błąd wysyłania powiadomienia: {response.status_code} - {response.text}")
        return False


def get_recent_activities(api_token, limit=5):
    url = f"https://intervals.icu/api/v1/athlete/activities?limit={limit}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "User-Agent": "intervals-connector/1.0"
    }

    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Błąd HTTP: {e} (status: {response.status_code})")
        if response.status_code == 403:
            print("Dostęp zabroniony: sprawdź token API i uprawnienia.")
        raise

    return response.json()

def main():
    api_token = os.getenv("INTERVALS_API_TOKEN")
    if not api_token:
        print("Nie znaleziono tokena INTERVALS_API_TOKEN w zmiennych środowiskowych.")
        return

    print("Pobieram ostatnie aktywności z Intervals.icu...")
    try:
        activities = get_recent_activities(api_token)
    except Exception as e:
        print(f"Nie udało się pobrać aktywności: {e}")
        return

    print(f"Pobrano {len(activities)} aktywności:")
    for i, activity in enumerate(activities, 1):
        name = activity.get("name", "Bez nazwy")
        date = activity.get("start_date_local", "Brak daty")
        print(f"{i}. {name} - {date}")

    if activities:
        last_activity = activities[0]
        title = "Nowa aktywność na Intervals.icu"
        message = f"{last_activity.get('name', 'Brak nazwy')} - {last_activity.get('start_date_local', '')}"
        send_onesignal_push(title, message)

if __name__ == "__main__":
    main()
