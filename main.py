from flask import Flask, request
from scheduler import scheduler

app = Flask(__name__)

@app.route("/")
def index():
    return "ProfessorJoe Bot is running."

@app.route("/callback", methods=["POST"])
def callback():
    body = request.get_json()
    print("📥 Webhook 收到資料：", body)
    return "OK"

if __name__ == "__main__":
    scheduler.start()
    app.run()