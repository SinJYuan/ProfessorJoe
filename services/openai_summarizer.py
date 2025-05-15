from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def summarize_with_openai(articles):
    try:
        prompt = """
你是一位專業的投資分析師，請閱讀以下新聞標題，綜合出與台灣與美國股市有關的重要趨勢。

請以條列方式提供：
1. 今日總結（20~30字）
2. 潛在受益產業與相關個股（台股或美股）
3. 每檔個股建議（買進/觀望/賣出），請附簡短理由
4. 如有重大風險，請提醒投資人注意

請用繁體中文，字數不超過 150 字。
"""
        for i, article in enumerate(articles):
            prompt += f"{i+1}. {article['title']}\n"

        print("🧠 傳送至 OpenAI...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ OpenAI 摘要失敗：", e)
        return "（OpenAI 摘要失敗）"
