# 系統架構文件 (Architecture)：股票 LINE Bot

## 1. 系統總覽 (System Overview)
*   **高階架構描述**：
    本系統為一個基於 LINE Messaging API 的聊天機器人。使用者透過 LINE 用戶端發送訊息或點擊按鈕，LINE 伺服器會將事件 (Webhook) 轉發至我們的後端伺服器。後端伺服器接收到事件後，進行解析與處理（例如向外部股市 API 查詢即時股價、操作本地資料庫以更新自選股或提醒設定），最後將結果封裝為 Flex Message 回傳給使用者。此外，系統包含一個背景排程器 (Scheduler)，定時檢查使用者設定的「到價提醒」條件，達標時主動推送通知。
*   **技術棧 (Tech Stack)**：
    *   **後端框架：FastAPI**。選擇原因：具備極佳的非同步 (Async) 效能，能輕鬆滿足 LINE Webhook 要求的 2 秒內高併發回應速度，且內建 Pydantic 資料驗證與自動化 API 文件。
    *   **LINE 整合：`line-bot-sdk-python` (v3)**。選擇原因：LINE 官方提供的 SDK，支援非同步操作，且 v3 貼近最新的 OpenAPI 規範。
    *   **資料庫：SQLite + SQLAlchemy (ORM)**。選擇原因：作為輕量化的個人或中小型專案，SQLite 不需額外架設資料庫伺服器即可快速上線，搭配 SQLAlchemy 方便未來若需擴充（如轉移至 PostgreSQL）時可無縫轉移。
    *   **背景排程：APScheduler**。選擇原因：輕量級且可與 FastAPI 在同一行程內完美整合，適合執行每分鐘檢查股價的「到價提醒」任務。
    *   **股市 API**：可串接 `yfinance`、`twstock` 或 Fugle 富果 API，視需要取得即時報價與大盤資料。

## 2. 目錄結構 (Directory Structure)
```text
line_bot_0429/
├── docs/
│   ├── PRD.md                 # 產品需求文件
│   └── ARCHITECTURE.md        # 系統架構文件 (本文件)
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI 程式入口點，負責啟動伺服器與載入 Router
│   ├── config.py              # 環境變數管理 (載入 .env 檔案的 Token 等)
│   ├── database.py            # SQLite 連線設定與 Session 管理
│   ├── models.py              # SQLAlchemy ORM 資料表定義 (User, Watchlist, Alert)
│   ├── schemas.py             # Pydantic 驗證模型 (用於內部資料傳遞)
│   ├── crud.py                # 資料庫操作邏輯封裝 (Create, Read, Update, Delete)
│   ├── services/              # 核心商業邏輯與外部服務整合
│   │   ├── line_bot.py        # LINE SDK 初始化、Flex Message 樣板生成與發送
│   │   ├── stock_api.py       # 外部股市 API 請求與股價快取 (Cache) 邏輯
│   │   └── scheduler.py       # APScheduler 背景任務設定 (定期檢查到價提醒)
│   └── routers/               # API 路由
│       └── webhook.py         # LINE Webhook 接收端點 (`/callback`) 與事件處理 handler
├── .env                       # 環境變數設定檔 (機密資訊，不進版控)
├── .env.example               # 環境變數範例檔
├── requirements.txt           # Python 依賴套件清單
└── run.py                     # 啟動腳本 (執行 uvicorn)
```
*   **模組說明**：
    *   `services/`：隔離與外部系統溝通的邏輯，確保 `routers` 只處理 HTTP 請求的接收與回應，提高程式可維護性。
    *   `models.py` vs `schemas.py`：`models` 負責對接資料庫欄位；`schemas` 負責驗證資料結構。

## 3. 系統流程與介接 (System Flow & Integration)
*   **前後端互動方式**：
    *   **使用者主動請求**：使用者透過 LINE App 發送指令 -> LINE Server 發出 HTTP POST 請求至 FastAPI 的 `/callback` -> `WebhookHandler` 驗證簽章與解析事件 -> 呼叫對應的服務 (如 `stock_api.py` 查詢股價) -> 呼叫 `line_bot.py` 透過 API 回傳結果。
    *   **系統主動推播 (到價提醒)**：`scheduler.py` 內定義的定時任務每 1 分鐘觸發 -> 撈取 `models.Alert` 中未完成的條件 -> 批次呼叫 `stock_api.py` 取得當下股價 -> 判斷條件是否成立 -> 條件成立者，呼叫 `line_bot.py` 的 Push Message API 發送通知並更新 DB 狀態。
*   **核心組件圖/流程說明**：
    ```text
    [LINE App User]
          │ (Text / Postback)
          ▼
    [LINE Platform] ─────────(POST /callback)────────┐
          │                                          ▼
          │ (Push Message)                    [FastAPI Webhook Router]
          │                                          │ (Validate X-Line-Signature)
          ▲                                          ▼
    [LINE Bot API] ◄─────(Reply Message)────── [Event Handler]
                                                     │
               ┌─────────────────────────────────────┤
               ▼                                     ▼
        [Database (SQLite)]                 [Stock Service]
    (Read/Write User, Watchlist)             (Fetch API & Cache)
               ▲                                     │
               │                                     ▼
        [APScheduler] ◄────────────────────── [External Stock API]
    (Check price alerts per minute)          (e.g., Yahoo Finance)
    ```

## 4. 部署與基礎設施 (Deployment & Infrastructure)
*   **環境需求**：
    *   **開發環境**：本地端 Python 3.9+，使用 `ngrok` 將本地端 Port (例如 8000) 暴露至公網以接收 LINE Webhook 測試。
    *   **正式環境**：可運行 Python 的虛擬主機 (VPS) 或雲端平台 (PaaS)。
*   **部署策略**：
    *   **雲端平台部署 (推薦 Render 或 Railway)**：由於本專案包含背景排程器與本機 SQLite 資料庫，不建議部署於 Serverless 架構 (如 Vercel, AWS Lambda)，因為 Serverless 環境會在閒置時休眠，導致排程器中斷，且檔案系統通常為唯讀 (唯有 `/tmp` 可寫，但重啟會消失)。
    *   **VPS 部署 (如 Linode, AWS EC2, GCP e2-micro)**：可使用 Docker 打包整套應用程式，配合 Docker Compose 啟動，最為穩定且能保證 SQLite 資料持久性。
    *   **環境變數管理**：正式環境需於平台介面或 `.env` 設定 `LINE_CHANNEL_SECRET` 與 `LINE_CHANNEL_ACCESS_TOKEN` 等機密資料。
