#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask 應用工廠模組

負責創建並配置 Flask 應用程序實例，應用所有中間件和路由藍圖
"""

import logging
from typing import Optional
from flask import Flask

from src.config import Config
from src.utils import setup_logging

logger = logging.getLogger(__name__)


def create_app(config: Optional[Config] = None) -> Flask:
    """
    創建並配置 Flask 應用程式

    Args:
        config: 應用配置物件，若為 None 則使用預設配置

    Returns:
        已配置的 Flask 應用程式實例

    Raises:
        ValueError: 缺少必要的環境變數時拋出異常
    """
    if config is None:
        config = Config

    # ============ Fail-Fast 驗證 ============
    _validate_required_config(config)

    # ============ 設置日誌 ============
    setup_logging(
        log_level=config.get_log_level(),
        log_file=config.get_log_file(),
    )
    logger.info("開始初始化 Flask 應用程式...")

    # ============ 創建 Flask 應用 ============
    app = Flask(__name__)
    app.config.update(
        DEBUG=config.get_debug(),
        SECRET_KEY=config.get_secret_key(),
        JSON_SORT_KEYS=False,
        JSONIFY_PRETTYPRINT_REGULAR=True,
    )

    # ============ 應用配置到 Flask ============
    app.config["GEMINI_MODEL"] = config.get_gemini_model()
    app.config["GEMINI_API_KEY"] = config.get_gemini_api_key()
    app.config["LINE_CHANNEL_SECRET"] = config.get_line_channel_secret()
    app.config["LINE_CHANNEL_ACCESS_TOKEN"] = config.get_line_channel_access_token()

    # ============ 註冊路由和藍圖 ============
    _register_routes(app)
    _register_blueprints(app)

    logger.info("✅ Flask 應用程式初始化完成")
    return app


def _validate_required_config(config: Config) -> None:
    """
    驗證必要的環境配置

    Args:
        config: 應用配置物件

    Raises:
        ValueError: 缺少必要配置時拋出異常
    """
    required_configs = {
        "GEMINI_API_KEY": config.get_gemini_api_key(),
        "LINE_CHANNEL_SECRET": config.get_line_channel_secret(),
        "LINE_CHANNEL_ACCESS_TOKEN": config.get_line_channel_access_token(),
    }

    missing_configs = [
        name for name, value in required_configs.items() if not value
    ]

    if missing_configs:
        error_msg = f"啟動失敗：缺少必要的環境變數 {', '.join(missing_configs)}"
        logger.error(error_msg)
        raise ValueError(error_msg)


def _register_routes(app: Flask) -> None:
    """
    註冊應用基本路由

    Args:
        app: Flask 應用程式實例
    """

    @app.get("/health")
    def health():
        """健康檢查端點"""
        return {"status": "OK", "service": "AI Language Bridge"}, 200

    @app.get("/info")
    def info():
        """應用信息端點"""
        return {
            "name": "AI Language Bridge LINE Bot",
            "version": "1.0.0",
            "status": "running",
        }, 200

    logger.info("✅ 基本路由已註冊")


def _register_blueprints(app: Flask) -> None:
    """
    註冊應用藍圖

    Args:
        app: Flask 應用程式實例
    """
    from src.line_bot.handler import create_line_bot_handler

    # 全局用戶偏好設置字典
    # 結構: {user_id: "ja" | "en" | "multi"}
    user_prefs = {}

    webhook_bp = create_line_bot_handler(user_prefs)
    app.register_blueprint(webhook_bp)

    logger.info("✅ LINE Webhook 藍圖已註冊")
