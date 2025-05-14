from flask import Flask, request
import requests, os, json
from apscheduler.schedulers.background import BackgroundScheduler
import openai

# 環境變數讀取
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

# 發送訊息給 Line
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
    requests.post(url, headers=headers, json=body)

# 抓新聞 + 整理成摘要
import os
import requests

def fetch_and_summarize_news():
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        print("❌ NEWSAPI_KEY not set")
        return

    news_url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&pageSize=5&apiKey={api_key}"

    try:
        response = requests.get(news_url)
        print(f"✅ NewsAPI status: {response.status_code}")
        print("🔍 Response text preview:", response.text[:200])  # 只印前200字

        if response.status_code != 200:
            print("❌ Failed to fetch news")
            return

        data = response.json()

        if data.get("status") != "ok":
            print("❌ API response not ok:", data)
            return

        articles = data.get("articles", [])
        if not articles:
            print("ℹ️ No articles found.")
            return

        summary = ""
        for i, article in enumerate(articles):
            summary += f"🔹 {article['title']}\n{article['url']}\n\n"

        print("✅ Summary:\n", summary)

        # 🔁 把這裡換成推播給 LINE 的函式即可
        # send_line_push(summary)

    except Exception as e:
        print("❌ Exception while fetching news:", str(e))


# 每 30 分鐘執行一次
scheduler.add_job(fetch_and_summarize_news, 'interval', minutes=1)

@app.route("/")
def index():
    return "ProfessorJoe is running."

@app.route("/callback", methods=["POST"])
def callback():
    body = request.get_json()
    print("📥 Webhook 收到資料：", json.dumps(body, indent=2))
    return "OK"

if __name__ == "__main__":
    app.run()
