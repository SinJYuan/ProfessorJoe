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
def fetch_and_summarize_news():
    print("⏰ 抓取新聞中...")
    news_url = (
        f"https://newsapi.org/v2/top-headlines?"
        f"category=business&language=en&pageSize=5&apiKey={NEWSAPI_KEY}"
    )
    res = requests.get(news_url).json()
    articles = res.get("articles", [])

    headlines = "\n".join([f"{i+1}. {a['title']}" for i, a in enumerate(articles)])
    full_text = "你是財經分析師，將簡要摘要下列新聞，並評估對台股和美股可能的短期影響。\n" + headlines

    # 用 OpenAI 生成摘要
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": full_text}]
        )
        summary = response.choices[0].message.content.strip()
        push_to_line("📈 每日財經整理來囉：\n\n" + summary)
    except Exception as e:
        push_to_line("❌ OpenAI 回應失敗：" + str(e))

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
