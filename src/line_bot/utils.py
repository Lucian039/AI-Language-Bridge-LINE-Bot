#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LINE Bot 工具函數模組

此模組提供 LINE Bot 相關的輔助函數，包括：
- 消息格式化
- 消息驗證
- 語言代碼解析等

這些函數與 LINE API 無關，純粹用於數據處理和驗證。
"""

import logging
from typing import Dict, Optional
from src.config import Config

logger = logging.getLogger(__name__)


def validate_message_length(message: str) -> bool:
    """
    驗證消息長度是否在允許範圍內。
    
    Args:
        message: 要驗證的消息文本
        
    Returns:
        bool: 消息長度有效時為 True，否則為 False
        
    Example:
        >>> validate_message_length("Hello World")
        True
        >>> validate_message_length("x" * 2000)
        False
    """
    if not message or not isinstance(message, str):
        return False
    
    message_length = len(message)
    max_length = Config.get_max_message_length()
    
    return message_length <= max_length


def format_translation_message(
    original_text: str,
    translation: str,
    source_lang: str = "unknown",
    target_lang: str = "unknown"
) -> str:
    """
    Format translation reply message.
    
    This function formats the original text, translation result and language information
    into a user-friendly message.
    
    Args:
        original_text: Original text
        translation: Translated text
        source_lang: Source language name (default: "unknown")
        target_lang: Target language name (default: "unknown")
        
    Returns:
        str: Formatted message string
        
    Example:
        >>> msg = format_translation_message(
        ...     "Hello",
        ...     "你好",
        ...     "English",
        ...     "Traditional Chinese"
        ... )
        >>> print(msg)
        《 English → Traditional Chinese 》
        Original: Hello
        Translation: 你好
    """
    formatted_message = (
        f"《 {source_lang} → {target_lang} 》\n"
        f"Original: {original_text}\n"
        f"Translation: {translation}"
    )
    
    return formatted_message


def extract_language_code(language_name: str) -> Optional[str]:
    """
    從語言名稱提取語言代碼。
    
    此函數支持多種語言名稱格式，包括英文名稱、中文名稱等。
    
    Args:
        language_name: 語言名稱 (e.g., "English", "Chinese", "日本語")
        
    Returns:
        Optional[str]: 對應的語言代碼 (e.g., "en", "zh-TW", "ja")，
                       如果找不到則返回 None
                       
    Example:
        >>> extract_language_code("English")
        'en'
        >>> extract_language_code("繁體中文")
        'zh-TW'
        >>> extract_language_code("Unknown")
        None
    """
    language_map = {
        # 英文名稱
        "English": "en",
        "Chinese": "zh",
        "Traditional Chinese": "zh-TW",
        "Simplified Chinese": "zh-CN",
        "Japanese": "ja",
        "Korean": "ko",
        "Spanish": "es",
        "French": "fr",
        "German": "de",
        "Russian": "ru",
        
        # 中文名稱
        "英文": "en",
        "中文": "zh",
        "繁體中文": "zh-TW",
        "簡體中文": "zh-CN",
        "日文": "ja",
        "日語": "ja",
        "韓文": "ko",
        "韓語": "ko",
        "西班牙文": "es",
        "法文": "fr",
        "德文": "de",
        "俄文": "ru",
    }
    
    return language_map.get(language_name)


def sanitize_text(text: str) -> str:
    """
    清淨文本，移除潛在的危險字符。
    
    此函數用於防止特定類型的注入攻擊和數據驗證。
    
    Args:
        text: 要清淨的文本
        
    Returns:
        str: 清淨後的文本
        
    Example:
        >>> sanitize_text("Hello\\x00World")
        'HelloWorld'
    """
    # 移除控制字符
    cleaned = "".join(char for char in text if ord(char) >= 32 or char in "\n\r\t")
    return cleaned.strip()


def split_long_message(message: str, max_length: int = 2000) -> list:
    """
    將長消息分割成多個較短的消息。
    
    LINE Messaging API 對單一消息有長度限制，此函數將長文本
    分割成多個可發送的片段。
    
    Args:
        message: 要分割的消息
        max_length: 每段消息的最大長度 (預設: 2000)
        
    Returns:
        list: 分割後的消息列表
        
    Example:
        >>> msgs = split_long_message("x" * 5000, max_length=1000)
        >>> len(msgs)
        5
    """
    if len(message) <= max_length:
        return [message]
    
    messages = []
    current_pos = 0
    
    while current_pos < len(message):
        messages.append(message[current_pos:current_pos + max_length])
        current_pos += max_length
    
    return messages
