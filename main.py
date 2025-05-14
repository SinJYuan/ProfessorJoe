from flask import Flask, request, abort
from apscheduler.schedulers.background import BackgroundScheduler
import requests, os, json

# 環境變數方式儲存金鑰
LINE_TOKEN    = os.getenv("LINE_ACCESS_TOKEN")
NEWSAPI_KEY   = os.getenv("NEWSAPI_KEY")
OPENAI_APIKEY = os.getenv("OPENAI_API_KEY")
LINE_PUSH_URL = "https://api.line.me/v2/bot/message/broadcast"

headers_line = {
    "Authorization": f"Bearer {LINE_TOKEN}",
    "Content-Type":  "application/json"
}

def fetch_financial_news():
    url = ("https://newsapi.org/v2/top-headlines?"
           "category=business&language=en&pageSize=5&apiKey="+NEWSAPI_KEY)
    r = requests.get(url)
    return r.json().get("articles", [])

def summarize_and_analyze(articles):
    messages = [
        {"role":"system","content":
            "你是財經分析師，將簡要摘要下列新聞，並評估對台股和美股可能的短期影響。"}
    ]
    for a in articles:
        messages.append({"role":"user","content": f"標題：{a['title']}\n內文：{a['description']}"})
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "max_tokens": 400
    }
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization":f"Bearer {OPENAI_APIKEY}"},
        json=payload
    )
    return resp.json()["choices"][0]["message"]["content"]

def push_to_line(text):
    data = {
        "messages": [
            {"type":"text", "text": text}
        ]
    }
    requests.post(LINE_PUSH_URL, headers=headers_line, json=data)

def job():
    arts = fetch_financial_news()
    if not arts: 
        return
    summary = summarize_and_analyze(arts)
    push_to_line(summary)

# Flask app 主要用於接收 Webhook 驗證（如果需要）
app = Flask(__name__)
@app.route("/callback", methods=['POST'])
def callback():
    # 可做用戶回覆處理等
    return 'OK'

if __name__ == "__main__":
    # 啟動排程：每 30 分鐘執行一次
    scheduler = BackgroundScheduler()
    scheduler.add_job(job, 'interval', minutes=3)
    scheduler.start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
