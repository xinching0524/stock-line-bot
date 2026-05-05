# W11 作業：股票 LINE Bot

> **繳交方式**：將你的 GitHub repo 網址貼到作業繳交區
> **作業性質**：個人作業

---

## 作業目標

利用上週設計的 Skill，開發一個股票相關的 LINE Bot。
重點不是功能多寡，而是你設計的 **Skill 品質**——Skill 寫得越具體，AI 產出的程式碼就越接近可以直接執行。

---

## 功能要求（擇一實作）

| 功能 | 說明 |
| --- | --- |
| AI 分析股票 | 使用者說股票名稱，Gemini 給出分析 |
| 追蹤清單 | 儲存使用者的自選股清單到 SQLite |
| 查詢即時價格 | 整合 yfinance 或 twstock 取得股價 |

> 本專案實作了 **AI 分析股票** 與 **查詢即時價格** 的雙重功能，整合 `yfinance` 抓取股價並由 `Gemini` (google-genai) 進行分析。

---

## 繳交項目

你的 GitHub repo 需要包含：

| 項目 | 說明 |
| --- | --- |
| `app.py` | LINE Webhook + Gemini + SQLite 後端 |
| `requirements.txt` | 所有套件 |
| `.env.example` | 環境變數範本（不含真實 token） |
| `.agents/skills/` | 至少包含 `/linebot-implement` Skill |
| `README.md` | 本檔案（含心得報告） |
| `screenshots/result.png` | LINE Bot 對話截圖（至少一輪完整對話） |

---

## 專案結構

```
your-repo/
├── .agents/
│   └── skills/
│       ├── prd/SKILL.md
│       ├── linebot-implement/SKILL.md
│       └── commit/SKILL.md
├── docs/
│   └── PRD.md
├── screenshots/
│   └── result.png
├── app.py
├── database.py             ← SQLite 記錄對話
├── stock_ai_service.py     ← yfinance 與 Gemini 邏輯
├── requirements.txt
├── .env.example
└── README.md
```

> `.env` 和 `interactions.db` 不要 commit（已加入 `.gitignore`）

---

## 系統截圖

下方為股票 LINE Bot 的實際運行對話截圖：

- **LINE Bot 對話實測**
  <br>![LINE Bot 對話實測](screenshots/result.png)

---

## 啟動方式

```bash
# 1. 建立虛擬環境
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. 安裝套件
pip install -r requirements.txt

# 3. 設定環境變數
cp .env.example .env
# 編輯 .env，填入三個 token: LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN, GEMINI_API_KEY

# 4. 啟動 FastAPI
uvicorn app:app --reload
# 或直接執行 python app.py

# 5. 另開終端機啟動 ngrok
ngrok http 8000
# 複製 https 網址，填入 LINE Developers Console 的 Webhook URL（加上 /callback）
# 點「Verify」確認連線正常後，掃 QR Code 加好友開始測試
```

---

## 心得報告

**姓名**：辛晴
**學號**：D1150271

**Q1. 你在 `/linebot-implement` Skill 的「注意事項」寫了哪些規則？為什麼這樣寫？**

> 我在設定中明確規範了幾個核心技術條件：必須透過 yfinance 獲取股市數據，並搭配最新版的 google-genai 套件來呼叫 Gemini 進行解讀；另外也要求必須實作 SQLite 來儲存使用者的 userId。這樣設計主要是為了確保最終生成的程式碼能完全對齊這次作業的評分標準，同時也能建立一套穩定運作的即時股票分析系統。
---

**Q2. 你的 Skill 第一次執行後，AI 產出的程式直接能跑嗎？需要修改哪些地方？修改後有沒有更新 Skill？**

> 初次生成的程式碼邏輯基本可行，但在環境變數以及 LINE Webhook URL 的串接上遇到了一些阻礙（像是 Webhook 忘記啟用、Token 參數填寫有誤等）。此外，因為舊版的 google.generativeai 模組已經停用，我後來自行將程式碼修改為導入新版的 google-genai 套件，並指定使用 gemini-2.5-flash-lite 模型，這才順利排除了模型找不到 (404) 與伺服器大塞車 (503) 的報錯問題。

---

**Q3. 你遇到什麼問題是 AI 沒辦法自己解決、需要你介入處理的？**

>AI 完全沒辦法幫我處理「本地環境設定」跟「平台串接」，像是去 LINE Developers 申請帳號、拿 Token，還有用 ngrok 建立 HTTPS 通道把網址綁定到 Webhook，這些都要自己手動點擊操作。另外，在終端機遇到 pip 找不到指令，或是 ngrok 憑證不小心貼錯導致報錯閃退，這些本機環境的 debug 還是得靠自己實際操作跟排除。

---

**Q4. 如果你要把這個 LINE Bot 讓朋友使用，你還需要做什麼？**

我必須把這個 FastAPI 後端程式部署到雲端伺服器上（例如 Render 或 Heroku）並綁定固定的網域，同時也要考量 SQLite 資料庫在雲端部署時的儲存問題，確保大家的對話記憶不會因為伺服器重啟而消失。
