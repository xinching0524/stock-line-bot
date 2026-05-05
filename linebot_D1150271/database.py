import sqlite3
from datetime import datetime
import os

# 使用絕對路徑或相對路徑確保資料庫放在專案目錄下
DB_NAME = os.path.join(os.path.dirname(__file__), "interactions.db")

def init_db():
    """初始化資料庫與資料表"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            user_message TEXT NOT NULL,
            bot_reply TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def log_interaction(user_id: str, user_message: str, bot_reply: str):
    """記錄使用者的 userId 與互動對話"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO interactions (user_id, user_message, bot_reply, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (user_id, user_message, bot_reply, datetime.now()))
    conn.commit()
    conn.close()

# 匯入時自動初始化資料庫
init_db()
