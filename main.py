#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Language Bridge LINE Bot - 應用程式入口

這是整合 LINE Messaging API 與 Gemini AI 的翻譯機器人主程式。

狀態管理:
---------
此應用使用全局 user_prefs 字典管理用戶的翻譯模式设置：
- 鍵: user_id (LINE 用戶 ID)
- 值: "ja" (日文) | "en" (英文) | "multi" (中英日對照)
- 默認值: "ja" (日文模式)

快速選單功能:
-----------
- 用戶輸入 "選單" 或 "menu" 返回翻譯模式選擇菜單
- 用戶選擇後，user_prefs 被更新
- 後續翻譯將根據選擇的模式使用不同的 Prompt

使用方式:
    python main.py

環境變數需求:
    - LINE_CHANNEL_ACCESS_TOKEN: LINE 頻道的存取令牌
    - LINE_CHANNEL_SECRET: LINE 頻道的密鑰
    - GEMINI_API_KEY: Google Gemini API 密鑰
"""

# 標準庫
import os

# 第三方庫
from dotenv import load_dotenv
from flask import Flask

# 嚴格先載入環境變數，再匯入任何 app 自定義模組
load_dotenv(override=True)

# 專案模組（必須在 load_dotenv() 之後）
from app.config import Config
from app.handler import line_webhook_bp


def create_app():
    """
    創建並配置 Flask 應用程式。
    
    Returns:
        Flask: 已配置的 Flask 應用程式實例
        
    Raises:
        ValueError: 缺少必要的環境變數時拋出異常
    """
    
    # Fail-Fast: 啟動階段先驗證關鍵設定
    if not Config.GEMINI_API_KEY:
        raise ValueError(
            "啟動失敗：未設定 GEMINI_API_KEY。請在 .env 填入有效值。"
        )

    if not Config.LINE_CHANNEL_SECRET:
        raise ValueError(
            "啟動失敗：未設定 LINE_CHANNEL_SECRET。請在 .env 填入有效值。"
        )

    if not Config.LINE_CHANNEL_ACCESS_TOKEN:
        raise ValueError(
            "啟動失敗：未設定 LINE_CHANNEL_ACCESS_TOKEN。請在 .env 填入有效值。"
        )
    
    # 創建 Flask 應用
    app = Flask(__name__)
    app.config["GEMINI_MODEL"] = Config.GEMINI_MODEL
    app.config["SYSTEM_PROMPT"] = Config.SYSTEM_PROMPT
    
    # 註冊 LINE Webhook 路由
    app.register_blueprint(line_webhook_bp())

    @app.get("/health")
    def health():
        """健康檢查端點。"""
        return "OK", 200
    
    return app


if __name__ == "__main__":
    app = create_app()
    
    # 運行應用程式
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    
    print(f"[START] AI Language Bridge 翻譯機器人已啟動 (Port: {port})")
    app.run(host="0.0.0.0", port=port, debug=debug)
