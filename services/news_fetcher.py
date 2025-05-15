import requests
import feedparser
from config import NEWSAPI_KEY

def fetch_newsapi():
    try:
        url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&pageSize=5&apiKey={NEWSAPI_KEY}"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        }
        res = requests.get(url, headers=headers)
        data = res.json()
        articles = [
            {
                "title": a["title"],
                "source": a["source"]["name"],
                "url": a["url"],
                "published_at": a["publishedAt"]
            }
            for a in data.get("articles", [])
        ]
        return articles
    except Exception as e:
        print("❌ NewsAPI 錯誤：", e)
        return []

def fetch_google_rss():
    try:
        rss_url = "https://news.google.com/rss/search?q=business+stock+market&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        return [
            {
                "title": entry.title,
                "source": "Google News",
                "url": entry.link,
                "published_at": entry.published if "published" in entry else ""
            }
            for entry in feed.entries[:5]
        ]
    except Exception as e:
        print("❌ Google RSS 錯誤：", e)
        return []

def fetch_all_articles():
    return fetch_newsapi() + fetch_google_rss()