import os
import sys
from dotenv import load_dotenv
from fastapi import Request, FastAPI, HTTPException

import database
import stock_ai_service

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

# 載入 .env 檔案
load_dotenv()

# 確保環境變數已設定，切勿將機密資訊硬編碼在程式碼中！
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)

app = FastAPI(title="Stock LINE Bot")

@app.post("/callback")
async def callback(request: Request):
    # 取得 LINE 簽章
    signature = request.headers.get('X-Line-Signature', '')

    # 取得請求內容字串
    body = await request.body()
    body_decoded = body.decode('utf-8')

    # 驗證簽章並處理 webhook
    try:
        handler.handle(body_decoded, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        raise HTTPException(status_code=400, detail="Invalid signature.")

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text
    user_id = event.source.user_id
    
    # 1. 使用 Gemini AI 與 yfinance 處理訊息
    bot_reply = stock_ai_service.process_message(user_message)
    
    # 2. 將對話紀錄存入 SQLite 資料庫
    database.log_interaction(user_id, user_message, bot_reply)
    
    # 3. 回傳訊息給使用者
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=bot_reply)]
            )
        )

if __name__ == "__main__":
    import uvicorn
    # 本地端測試可用 uvicorn 啟動
    uvicorn.run(app, host="0.0.0.0", port=8000)
