#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pytest 配置檔

定義 pytest 的共享 fixtures 和配置
"""

import os
import sys
import pytest
from dotenv import load_dotenv

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

# 加載測試環境變數
load_dotenv(override=True)

# 設置測試環境
os.environ["FLASK_ENV"] = "testing"
os.environ["FLASK_DEBUG"] = "False"


@pytest.fixture
def app():
    """創建測試 Flask 應用程序"""
    from app.factory import create_app as real_create_app
    
    # 創建測試應用
    app = real_create_app()
    app.config["TESTING"] = True
    app.config["PROPAGATE_EXCEPTIONS"] = True
    
    return app


@pytest.fixture
def client(app):
    """創建測試客戶端"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """創建測試 CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def mock_user_prefs():
    """模擬用戶偏好字典"""
    return {
        "user_123": "ja",
        "user_456": "en",
        "user_789": "multi",
    }


@pytest.fixture
def sample_translation_request():
    """樣本翻譯請求"""
    from src.models import TranslationRequest
    
    return TranslationRequest(
        text="Hello, world!",
        target_language="ja",
        user_id="user_123",
    )


@pytest.fixture
def sample_line_message():
    """樣本 LINE 消息"""
    from src.models import LineMessage
    
    return LineMessage(
        user_id="U1234567890abcdef1234567890abcdef",
        message_id="100001",
        text="こんにちは",
        message_type="text",
        reply_token="nHuyWiB7yP5Zw52FIkcQT",
    )
