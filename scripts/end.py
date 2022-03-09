import requests
from config import API

def send_message():

    url = f"https://api.telegram.org/bot{API}/sendMessage"

    payload = {
        "text": "🚨 _Server Now Online_",
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
        "disable_notification": False,
        "chat_id": "1880154867"
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":

    send_message() 