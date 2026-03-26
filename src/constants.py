#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
應用常數定義模組

統一管理應用程序中使用的常數、枚舉值和預設值
"""

from enum import Enum
from typing import Final

# ==================== 翻譯模式常數 ====================
class TranslationMode(str, Enum):
    """翻譯模式枚舉"""
    JAPANESE = "ja"        # 日文翻譯
    ENGLISH = "en"         # 英文翻譯
    MULTILINGUAL = "multi" # 中英日對照

# 預設翻譯模式
DEFAULT_TRANSLATION_MODE: Final = TranslationMode.JAPANESE

# ==================== 語言常數 ====================
SUPPORTED_LANGUAGES: Final = {
    "ja": "日本語",
    "en": "English",
    "zh": "中文",
    "ko": "한국어",
    "es": "Español",
    "fr": "Français",
}

# ==================== Gemini 模型配置 ====================
DEFAULT_GEMINI_MODEL: Final = "gemini-1.5-flash"
GEMINI_MODEL_DEFAULT_TEMPERATURE: Final = 0.7
GEMINI_MODEL_DEFAULT_MAX_TOKENS: Final = 2048

# ==================== LINE Bot 配置 ====================
LINE_MAX_MESSAGE_LENGTH: Final = 5000  # LINE 文本消息上限
LINE_QUICK_REPLY_LIMIT: Final = 13     # LINE 快速回復按鈕上限

# ==================== 系統提示詞 ====================
SYSTEM_PROMPT_BASE: Final = "專業的多國語言翻譯助手，需自動偵測語言並提供道地、具備文化語境的翻譯"

TRANSLATION_PROMPTS: Final = {
    "ja": "請將用戶消息翻譯成日本語，只返回翻譯結果，不需要額外解釋。",
    "en": "Please translate the user message to English. Return only the translation without explanation.",
    "multi": "請提供中文、英文、日文三語對照翻譯，格式為：\n中文：[translated text]\n英文：[translated text]\n日文：[translated text]",
}

# ==================== 錯誤信息 ====================
ERROR_MESSAGES: Final = {
    "invalid_api_key": "API 金鑰配置錯誤",
    "network_error": "網路連線失敗",
    "api_error": "翻譯服務暫時無法使用",
    "invalid_input": "輸入格式錯誤",
    "rate_limit": "請求過於頻繁，請稍後再試",
}

# ==================== 日誌配置 ====================
LOG_LEVEL: Final = "INFO"
LOG_FORMAT: Final = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE: Final = "logs/app.log"
