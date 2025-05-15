# ProfessorJoe Line Bot

自動從多個新聞來源（NewsAPI、Google News RSS）擷取商業新聞，透過 OpenAI 分析成繁體中文投資建議，並推送至 LINE。

- 使用 Flask 架設 API server
- 每 60 分鐘定時執行新聞摘要與推播
- 可輕鬆擴充更多新聞來源

部署於 Render。
