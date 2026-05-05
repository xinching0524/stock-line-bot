# 資料庫結構與模型設計文件 (MODELS)

## 1. 資料庫選擇 (Database Choice)
*   **關聯式資料庫：SQLite**
    *   **選擇原因**：依據 `PRD.md` 與 `ARCHITECTURE.md` 的規劃，本專案屬於中小型流量或單機部署測試。SQLite 是非常輕量且無伺服器 (Serverless) 的關聯式資料庫，能完美契合 FastAPI 與 SQLAlchemy (ORM)，減少初期部屬與管理資料庫伺服器的複雜度。

## 2. 實體關聯圖與綱要 (ERD & Schema)
系統中包含四個主要實體 (Entities)：`users` (使用者)、`poems` (籤詩)、`draw_histories` (抽籤紀錄) 以及 `donations` (捐款紀錄)。

### 2.1 資料表：`users` (使用者表)
紀錄使用者的基礎資訊，作為關聯歷史紀錄的鍵值。
*   `id` (Integer) - **PK**。自動遞增。
*   `username` (String) - 登入用的簡易名稱識別，需設定為 **Unique** 防止撞名。
*   `created_at` (DateTime) - 帳號建立時間，預設為當下時間。

### 2.2 資料表：`poems` (籤詩庫)
儲存從 1 號開始的所有籤詩內容。
*   `id` (Integer) - **PK**。即籤號 (例如 1~60)。
*   `title` (String) - 籤詩的標題 (例如「第一籤」或典故名稱)。
*   `fortune_type` (String) - 吉凶 (例如：大吉、中平、下下)。
*   `content` (Text) - 古文籤詩原文。
*   `explanation` (Text) - 白話文解析內容。

### 2.3 資料表：`draw_histories` (抽籤歷史紀錄表)
紀錄誰在什麼時候，求問了什麼問題並得到了哪一支籤。
*   `id` (Integer) - **PK**。自動遞增。
*   `user_id` (Integer) - **FK** (關聯到 `users.id`)。
*   `poem_id` (Integer) - **FK** (關聯到 `poems.id`)。
*   `question` (String) - 使用者求問的問題內容（允許 Null，若使用者不想填寫的話）。
*   `created_at` (DateTime) - 抽籤時間，預設為當下時間。

### 2.4 資料表：`donations` (香油錢捐獻紀錄表)
紀錄使用者的虛擬捐獻資訊。
*   `id` (Integer) - **PK**。自動遞增。
*   `user_id` (Integer) - **FK** (關聯到 `users.id`)。
*   `amount` (Integer) - 捐獻的金額數字。
*   `message` (String) - 祈願祝福內容 / 供奉項目。
*   `created_at` (DateTime) - 捐款時間，預設為當下時間。

## 3. 基礎資料/預設資料 (Seed Data)
*   **初始資料 (`poems`)**：
    在系統第一次啟動建立資料表結構時，必須撰寫一個 Seed Script (例如 `seed.py`)，將 60 首甲子籤（或其他版本的觀音籤詩）自動預載寫進 `poems` 資料表中。否則系統抽籤邏輯將無法對應到任何實體內容。

## 4. 特殊考量 (Special Considerations)
*   **索引設計 (Indexing)**：
    *   在 `draw_histories(user_id)` 與 `donations(user_id)` 建立索引 (Index)。因為使用者在進入「我的歷史紀錄」頁面時，系統會頻繁利用 `user_id` 撈取這兩張表的所有關聯紀錄。
*   **資料安全與限制**：
    *   `users.username` 必須加上 `UniqueConstraint` 來確保不會有多個相同稱呼。
    *   為了避免惡意海量建立紀錄，實作階段必須倚靠 FastAPI 後端（例如 Pydantic）驗證使用者傳入的字串長度（`username` 最大長度 50，`question` 長度不超過 255 字）。
    *   （可選）由於使用 `username` 直接作為身分識別較不嚴謹，若後續要求隱私升級，可改用 JWT 或 Token 的方式綁定 Session 寫入 `user_id`。但在本專案當前規格下，單純使用 `username` 對應是可接受的範圍。
