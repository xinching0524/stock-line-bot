import os
import re
import yfinance as yf
from google import genai

def get_gemini_client():
    """取得 Gemini Client"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or "請" in api_key:
        return None
    return genai.Client(api_key=api_key)

def extract_stock_ticker(message: str) -> str:
    """從使用者訊息中提取股票代號"""
    # 找尋 4 位數台股代號 (例如 2330)
    match = re.search(r'\b\d{4}\b', message)
    if match:
        return f"{match.group(0)}.TW"
    
    # 找尋美股代號 (全大寫英文字母，如 AAPL, TSLA)
    match_us = re.search(r'\b[A-Z]{2,5}\b', message)
    if match_us:
        return match_us.group(0)
        
    return ""

def get_stock_info(ticker: str) -> str:
    """使用 yfinance 抓取即時股價資訊"""
    try:
        stock = yf.Ticker(ticker)
        # 抓取最近一天的資料
        data = stock.history(period="1d")
        if data.empty:
            return ""
            
        close_price = round(data['Close'].iloc[-1], 2)
        return f"({ticker} 最新收盤/即時價格: {close_price})"
    except Exception:
        return ""

def process_message(user_message: str) -> str:
    """處理使用者訊息，結合即時股價與 AI 分析"""
    client = get_gemini_client()
    if not client:
        return "系統尚未設定 Gemini API Key，請先於 .env 檔案中設定 GEMINI_API_KEY。"

    # 1. 嘗試擷取股票代號並取得即時股價
    ticker = extract_stock_ticker(user_message)
    realtime_price_info = ""
    if ticker:
        realtime_price_info = get_stock_info(ticker)

    # 2. 構建給 AI 的 Prompt
    prompt = f"""
你是一位專業且友善的股票分析師與理財顧問 LINE Bot。
使用者傳送的訊息是：「{user_message}」

{f'系統自動抓取到的即時市場資訊：{realtime_price_info}' if realtime_price_info else ''}

請遵循以下規則回應：
1. 必須使用「繁體中文」回答。
2. 若使用者有詢問特定股票，請基於系統提供的即時資訊或你的知識給予簡短分析。
3. 若使用者只是打招呼，請親切回覆並引導他們詢問股票（例如輸入「台積電」或「2330」）。
4. 請注意免責聲明：在分析結尾加上一句簡短的提醒「以上分析僅供參考，投資需謹慎評估風險」。
5. 回覆長度請保持在 LINE 適合閱讀的長度（約 100-200 字以內），適當使用 Emoji 增加親切感。
"""

    # 3. 呼叫 Gemini 產生回覆
    try:
        # 使用速度較快且支援度廣的模型
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API 錯誤: {e}")
        return "抱歉，AI 腦袋稍微當機了，請稍後再試一次！"
