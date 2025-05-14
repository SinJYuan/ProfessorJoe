from flask import Flask, request
import requests, os, json
from apscheduler.schedulers.background import BackgroundScheduler
from openai import OpenAI  # 新版用法

# ------------------ 環境變數 ------------------
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 初始化 OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY)

# ------------------ 初始化 ------------------
app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

# ------------------ 傳送 Line 訊息 ------------------
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
    response = requests.post(url, headers=headers, json=body)
    print(f"📤 Line push status: {response.status_code}")
    print("📤 Line response:", response.text)

# ------------------ 使用 OpenAI 進行摘要 ------------------
def summarize_with_openai(articles):
    try:
        prompt = "以下是今天的商業新聞標題，請幫我用繁體中文整理出重點摘要，然後條列出幾檔相關台股美股的標的，並給出你的看法來建議買進或賣出，回答在150字以內：\n\n"
        for i, article in enumerate(articles):
            prompt += f"{i+1}. {article['title']}\n"

        print("🧠 Sending to OpenAI...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            temperature=0.7,
            max_tokens=300
        )
        summary = response.choices[0].message.content.strip()
        print("✅ OpenAI summary done.")
        return summary
    except Exception as e:
        print("❌ Error during OpenAI summarization:", str(e))
        return "（OpenAI 摘要失敗）"

# ------------------ 抓新聞 + 摘要 ------------------
def fetch_and_summarize_news():
    print("🔄 開始執行新聞摘要任務")
    if not NEWSAPI_KEY:
        print("❌ NEWSAPI_KEY not found.")
        return

    news_url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&pageSize=5&apiKey={NEWSAPI_KEY}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
        "Referer": "https://newsapi.org/",
        "Origin": "https://newsapi.org"
    }

    try:
        print("🌐 正在向 NewsAPI 發送請求...")
        response = requests.get(news_url, headers=headers)
        print(f"📥 NewsAPI 回應狀態: {response.status_code}")

        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            print("❌ NewsAPI 錯誤狀態：", data)
            return

        articles = data.get("articles", [])
        if not articles:
            print("ℹ️ 沒有找到新聞。")
            return

        print(f"📰 共獲得 {len(articles)} 則新聞。")
        ai_summary = summarize_with_openai(articles)

        final_message = "📢 今日商業新聞摘要：\n" + ai_summary
        push_to_line(final_message)

    except requests.exceptions.HTTPError as http_err:
        print("❌ HTTP 錯誤：", http_err)
    except requests.exceptions.RequestException as req_err:
        print("❌ 請求錯誤：", req_err)
    except Exception as e:
        print("❌ 未知錯誤：", str(e))

# ------------------ 定時任務 ------------------
scheduler.add_job(fetch_and_summarize_news, 'interval', minutes=60, next_run_time=datetime.now())

# ------------------ 路由 ------------------
@app.route("/")
def index():
    return "ProfessorJoe is running."

@app.route("/callback", methods=["POST"])
def callback():
    body = request.get_json()
    print("📥 Webhook 收到資料：", json.dumps(body, indent=2))
    return "OK"

# ------------------ 啟動 ------------------
if __name__ == "__main__":
    app.run()
