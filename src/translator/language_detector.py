#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
語言檢測模組

此模組提供自動語言檢測功能，用於判斷文本所用的語言。

主要功能：
- 使用 langdetect 庫進行語言檢測
- 提供語言代碼和語言名稱的映射
- 錯誤處理和備默認值

支持的語言：主要的全球語言
"""

import logging
from typing import Dict, Optional
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

logger = logging.getLogger(__name__)

# 設置 langdetect 的隨機種子以確保一致的結果
DetectorFactory.seed = 0


class LanguageDetector:
    """
    語言檢測器類。
    
    使用 langdetect 庫檢測文本所用的語言，
    並提供語言代碼和名稱的轉換功能。
    
    Attributes:
        language_names (dict): 語言代碼到名稱的映射
    """
    
    # 語言代碼到名稱的映射表
    LANGUAGE_NAMES = {
        "en": "English",
        "zh-cn": "Simplified Chinese",
        "zh-tw": "Traditional Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "ar": "Arabic",
        "th": "Thai",
        "vi": "Vietnamese",
        "tr": "Turkish",
        "pl": "Polish",
        "nl": "Dutch",
        "hi": "Hindi",
        "id": "Indonesian",
        "uk": "Ukrainian",
    }
    
    def __init__(self):
        """初始化語言檢測器。"""
        pass
    
    def detect_language(self, text: str) -> Dict[str, str]:
        """
        檢測文本的語言。
        
        此方法使用 langdetect 庫自動檢測給定文本所用的語言。
        如果檢測失敗，將返回預設值（English）。
        
        Args:
            text: 要檢測語言的文本
            
        Returns:
            Dict[str, str]: 包含以下鍵值的字典：
                - language (str): 語言代碼 (e.g., "en", "zh-tw")
                - language_name (str): 語言名稱 (e.g., "English")
                - confidence (str): 檢測的信心程度
                
        Example:
            >>> detector = LanguageDetector()
            >>> result = detector.detect_language("Hello World")
            >>> print(result)
            {
                'language': 'en',
                'language_name': 'English',
                'confidence': '檢測成功'
            }
            
        Note:
            - 檢測結果的準確性取決於文本長度
            - 較短的文本可能檢測不準確
            - 混合多種語言的文本可能只檢測到主要語言
        """
        if not text or not isinstance(text, str):
            logger.warning("無效的輸入文本用於語言檢測")
            return {
                "language": "en",
                "language_name": "English",
                "confidence": "參數無效，使用預設"
            }
        
        try:
            # 使用 langdetect 檢測語言
            detected_code = detect(text)
            
            # 標準化語言代碼（某些情況下 langdetect 返回 "zh-cn" 或 "zh-tw"）
            lang_code = self._normalize_language_code(detected_code)
            lang_name = self.LANGUAGE_NAMES.get(lang_code, lang_code.upper())
            
            logger.debug(f"檢測到語言: {lang_code} ({lang_name})")
            
            return {
                "language": lang_code,
                "language_name": lang_name,
                "confidence": "檢測成功"
            }
            
        except LangDetectException as e:
            logger.warning(f"語言檢測失敗: {str(e)}，使用預設值")
            return {
                "language": "en",
                "language_name": "English",
                "confidence": "檢測失敗，使用預設"
            }
        except Exception as e:
            logger.error(f"語言檢測發生異常: {str(e)}", exc_info=True)
            return {
                "language": "en",
                "language_name": "English",
                "confidence": "發生異常，使用預設"
            }
    
    def _normalize_language_code(self, code: str) -> str:
        """
        標準化語言代碼。
        
        某些情況下，langdetect 返回的代碼格式不一致。
        此方法將其轉換為一致的格式。
        
        Args:
            code: 原始語言代碼
            
        Returns:
            str: 標準化後的語言代碼
            
        Example:
            >>> detector = LanguageDetector()
            >>> detector._normalize_language_code("zh-CN")
            'zh-cn'
        """
        code = code.lower()
        
        # 標準化中文代碼
        if code in ["zh", "zh-hans"]:
            return "zh-cn"
        elif code == "zh-hant":
            return "zh-tw"
        
        return code
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        取得支持的語言列表。
        
        Returns:
            Dict[str, str]: 語言代碼到名稱的映射
            
        Example:
            >>> detector = LanguageDetector()
            >>> langs = detector.get_supported_languages()
            >>> print(langs)
            {'en': 'English', 'zh-cn': 'Simplified Chinese', ...}
        """
        return self.LANGUAGE_NAMES.copy()
    
    def is_language_supported(self, language_code: str) -> bool:
        """
        檢查是否支持某個語言。
        
        Args:
            language_code: 語言代碼
            
        Returns:
            bool: 如果支持該語言返回 True，否則返回 False
            
        Example:
            >>> detector = LanguageDetector()
            >>> detector.is_language_supported("en")
            True
            >>> detector.is_language_supported("unknown")
            False
        """
        return language_code.lower() in self.LANGUAGE_NAMES
