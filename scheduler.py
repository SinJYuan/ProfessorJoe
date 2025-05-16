from apscheduler.schedulers.background import BackgroundScheduler
from services.news_fetcher import aggregate_news_sources
from services.openai_summarizer import summarize_with_openai
from services.line_messenger import push_to_line
from datetime import datetime

scheduler = BackgroundScheduler()

def job():
    print("🔄 執行定時摘要任務")
    articles = aggregate_news_sources()
    if not articles:
        print("⚠️ 無新聞可供摘要")
        return
    summary = summarize_with_openai(articles)
    message = "📢 今日商業新聞摘要：\n" + summary
    push_to_line(message)

scheduler.add_job(job, 'interval', minutes=60, next_run_time=datetime.now())
