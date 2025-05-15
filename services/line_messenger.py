import requests
from config import LINE_ACCESS_TOKEN

def push_to_line(message):
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    body = {
        "messages": [{
            "type": "text",
            "text": message
        }]
    }
    try:
        res = requests.post(url, headers=headers, json=body)
        res.raise_for_status()
        print(f"📤 Line 推播成功 ({res.status_code})")
    except Exception as e:
        print("❌ LINE 推播錯誤：", e)
