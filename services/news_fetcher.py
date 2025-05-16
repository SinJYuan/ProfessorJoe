import os
import requests
import feedparser

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

def fetch_newsapi():
    if not NEWSAPI_KEY:
        print("❌ NEWSAPI_KEY not found.")
        return []

    news_url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&pageSize=5&apiKey={NEWSAPI_KEY}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
        "Referer": "https://newsapi.org/",
        "Origin": "https://newsapi.org"
    }
    articles = []
    try:
        print("🌐 正在向 NewsAPI 發送請求...")
        response = requests.get(news_url, headers=headers)
        print(f"📥 NewsAPI 回應狀態: {response.status_code}")
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            print("❌ NewsAPI 錯誤狀態：", data)
            return []

        for article in data.get("articles", []):
            articles.append({
                "source": "NewsAPI",
                "title": article.get("title", ""),
                "url": article.get("url", "")
            })
        print(f"📰 NewsAPI 擷取到 {len(articles)} 則新聞。")
        return articles

    except requests.exceptions.RequestException as e:
        print("❌ NewsAPI 請求錯誤：", e)
        return []

def fetch_google_news():
    print("📡 擷取 Google News RSS")
    rss_url = "https://news.google.com/rss/search?q=business+stocks&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    articles = []
    try:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:5]:
            articles.append({
                "source": "Google News",
                "title": entry.title,
                "url": entry.link
            })
        print(f"✅ Google News 擷取 {len(articles)} 則新聞。")
        return articles
    except Exception as e:
        print("❌ Google News RSS 擷取錯誤:", e)
        return []

def fetch_yahoo_rss():
    print("📡 擷取 Yahoo 財經 RSS")
    rss_urls = [
        "https://tw.stock.yahoo.com/rss",             # 台股新聞
        "https://tw.stock.yahoo.com/rss/us-stock",    # 美股新聞
        "https://tw.stock.yahoo.com/rss/world",       # 國際財經
    ]

    all_articles = []
    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:  # 每個來源最多取3篇
                all_articles.append({
                    "source": "Yahoo Finance",
                    "title": entry.title,
                    "url": entry.link
                })
        except Exception as e:
            print(f"❌ Yahoo RSS 擷取錯誤: {e}")

    print(f"✅ Yahoo 財經共擷取 {len(all_articles)} 則新聞")
    return all_articles

def aggregate_news_sources():
    news = []
    #news += fetch_newsapi()
    news += fetch_google_news()
    news += fetch_yahoo_rss()
    return news