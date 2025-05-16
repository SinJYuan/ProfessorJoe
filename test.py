from services.news_fetcher import aggregate_news_sources

def test_fetch_all_sources():
    print("🔍 測試新聞來源擷取...")
    articles = aggregate_news_sources()
    print(f"\n📊 總共擷取到 {len(articles)} 則新聞。\n")
    for i, article in enumerate(articles, 1):
        print(f"{i}. [{article['source']}] {article['title']}")

if __name__ == "__main__":
    test_fetch_all_sources()
