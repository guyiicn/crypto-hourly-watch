import html

import requests

from . import config


def send(text: str) -> None:
    if not config.TG_BOT_TOKEN or not config.TG_CHAT_ID:
        print("TG not configured; message preview below:")
        print(text)
        return
    url = f"https://api.telegram.org/bot{config.TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TG_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    r = requests.post(url, json=payload, timeout=15)
    if r.status_code != 200:
        print(f"TG send failed: {r.status_code} {r.text}")


def esc(s: str) -> str:
    return html.escape(s, quote=False)
