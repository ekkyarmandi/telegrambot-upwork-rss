import requests
from scripts.config import API

def send_message():

    url = f"https://api.telegram.org/bot{API}/sendMessage"

    payload = {
        "text": "📴 _Server is Now Offline_",
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
        "disable_notification": False,
        "chat_id": "1880154867"
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    resp = requests.post(url, json=payload, headers=headers)
    print(resp.json())

if __name__ == "__main__":

    send_message()