#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具函數模組

統一管理應用程序中的工具函數和輔助方法
"""

import logging
from typing import Optional, Dict, Any

__all__ = [
    'setup_logging',
    'format_message',
    'truncate_text',
    'parse_language_code',
]


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
) -> None:
    """
    配置應用日誌

    Args:
        log_level: 日誌級別 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日誌文件路徑，若為 None 則只輸出到控制台
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    if log_file:
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(),
            ],
        )
    else:
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
        )


def format_message(
    content: str,
    format_type: str = "plain",
    **kwargs,
) -> str:
    """
    格式化消息內容

    Args:
        content: 消息內容
        format_type: 格式類型 (plain, markdown, json)
        **kwargs: 額外格式參數

    Returns:
        格式化後的消息
    """
    if format_type == "plain":
        return content.strip()
    
    if format_type == "markdown":
        return f"```\n{content}\n```"
    
    if format_type == "json":
        import json
        try:
            return json.dumps(json.loads(content), indent=2, ensure_ascii=False)
        except Exception:
            return content
    
    return content


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """
    截斷文本到指定長度

    Args:
        text: 原始文本
        max_length: 最大長度
        suffix: 尾部標記

    Returns:
        截斷後的文本
    """
    if len(text) <= max_length:
        return text
    
    truncated_length = max_length - len(suffix)
    return text[:truncated_length] + suffix


def parse_language_code(text: Optional[str]) -> Optional[str]:
    """
    解析語言代碼

    Args:
        text: 原始文本

    Returns:
        標準化後的語言代碼，或 None
    """
    if not text:
        return None
    
    code = text.lower().strip()
    
    # 常見語言代碼映射
    language_map = {
        "chinese": "zh",
        "中文": "zh",
        "english": "en",
        "英文": "en",
        "japanese": "ja",
        "日文": "ja",
        "日本語": "ja",
        "korean": "ko",
        "韓文": "ko",
        "spanish": "es",
        "西班牙文": "es",
        "french": "fr",
        "法文": "fr",
    }
    
    return language_map.get(code, code if len(code) == 2 else None)


def safe_get_dict_value(
    data: Dict[str, Any],
    key: str,
    default: Any = None,
    value_type: type = None,
) -> Any:
    """
    安全地從字典獲取值

    Args:
        data: 源字典
        key: 鍵名
        default: 默認值
        value_type: 值類型（可選的類型檢查）

    Returns:
        字典中的值或默認值
    """
    try:
        value = data.get(key, default)
        
        if value_type and value is not None:
            return value_type(value)
        
        return value
    except (KeyError, ValueError, TypeError):
        return default
