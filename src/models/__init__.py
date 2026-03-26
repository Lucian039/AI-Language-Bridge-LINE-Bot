#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
數據模型模組

定義應用程序中使用的數據結構和類型
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime

__all__ = [
    'TranslationRequest',
    'TranslationResponse',
    'UserPreference',
    'LineMessage',
]


@dataclass
class TranslationRequest:
    """翻譯請求數據模型"""
    text: str
    source_language: Optional[str] = None
    target_language: str = "ja"
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """驗證請求數據"""
        if not self.text or not self.text.strip():
            raise ValueError("翻譯文本不能為空")
        if len(self.text) > 5000:
            raise ValueError("翻譯文本超過最大長度限制(5000字符)")


@dataclass
class TranslationResponse:
    """翻譯响應數據模型"""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    model: str = "gemini-1.5-flash"
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time_ms: Optional[float] = None
    error: Optional[str] = None

    def is_success(self) -> bool:
        """判斷翻譯是否成功"""
        return self.error is None


@dataclass
class UserPreference:
    """用戶偏好設定數據模型"""
    user_id: str
    translation_mode: str = "ja"  # ja, en, multi
    language_source: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    custom_settings: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "user_id": self.user_id,
            "translation_mode": self.translation_mode,
            "language_source": self.language_source,
            "custom_settings": self.custom_settings,
        }


@dataclass
class LineMessage:
    """LINE 消息數據模型"""
    user_id: str
    message_id: str
    text: str
    message_type: str = "text"
    timestamp: datetime = field(default_factory=datetime.now)
    reply_token: Optional[str] = None

    def __str__(self) -> str:
        return f"LineMessage(user_id={self.user_id}, text={self.text[:50]}...)"
