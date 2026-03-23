#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gemini AI 翻譯引擎模組

此模組使用 Google Gemini API 提供翻譯服務。

主要功能：
- 調用 Gemini 模型進行文本翻譯
- 自動語言檢測
- 錯誤處理和重試機制
- 結果驗證和格式化

遵循模組化設計，翻譯邏輯完全獨立於 LINE Bot。
"""

import logging
from typing import Dict, Optional
import google.genai as genai
from src.config import Config
from src.translator.language_detector import LanguageDetector

logger = logging.getLogger(__name__)


def _normalize_gemini_error_message(raw_error: str) -> Dict[str, str]:
    """Map raw Gemini errors to stable app-level error codes/messages."""
    err_upper = raw_error.upper()

    if "429" in raw_error or "RESOURCE_EXHAUSTED" in err_upper:
        return {
            "error_code": "quota_exceeded",
            "error": "Gemini 配額已用盡，請稍後再試。"
        }

    if "503" in raw_error or "UNAVAILABLE" in err_upper:
        return {
            "error_code": "service_unavailable",
            "error": "Gemini 服務暫時忙碌，請稍後再試。"
        }

    if "404" in raw_error or "NOT_FOUND" in err_upper:
        return {
            "error_code": "model_not_found",
            "error": "Gemini 模型不可用，請檢查模型設定。"
        }

    return {
        "error_code": "unknown_error",
        "error": "翻譯服務發生未知錯誤，請稍後再試。"
    }


class GeminiTranslator:
    """
    使用 Google Gemini API 的翻譯引擎。
    
    此類負責初始化 Gemini 客戶端並提供翻譯方法。
    支持自動語言檢測和多語言翻譯。
    
    Attributes:
        model_name (str): 使用的 Gemini 模型名稱
        language_detector (LanguageDetector): 語言檢測器實例
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        """
        初始化 Gemini 翻譯器。
        
        Args:
            api_key: Google Gemini API 密鑰，默認使用配置中的值
            model_name: Gemini 模型名稱，預設從配置中讀取（gemini-1.5-flash）
            
        Raises:
            ValueError: 當 API 密鑰為空時拋出異常
        """
        self.api_key = api_key or Config.get_gemini_api_key()
        self.model_name = model_name or Config.get_gemini_model()
        fallback_models = Config.get_gemini_fallback_models()
        model_chain = [self.model_name] + fallback_models
        # 去重並保持順序，避免重複嘗試同一個模型
        self.model_candidates = list(dict.fromkeys(model_chain))
        
        if not self.api_key:
            raise ValueError("Gemini API 密鑰未設置")
        
        # 配置 Gemini API（新 SDK）
        self.client = genai.Client(api_key=self.api_key)
        self.language_detector = LanguageDetector()
        
        logger.info(
            "Gemini 翻譯器已初始化 (主模型: %s, 備援模型: %s)",
            self.model_name,
            self.model_candidates[1:]
        )

    def _generate_content_with_fallback(self, prompt: str) -> Dict[str, any]:
        """依序嘗試主模型與備援模型，直到成功或全部失敗。"""
        attempts = []

        for index, model_name in enumerate(self.model_candidates):
            try:
                response = self.client.models.generate_content(
                    model=f"models/{model_name}",
                    contents=prompt
                )

                return {
                    "success": True,
                    "response": response,
                    "model": model_name,
                    "fallback_used": index > 0,
                    "attempts": attempts,
                }
            except Exception as e:
                raw_error = str(e)
                normalized = _normalize_gemini_error_message(raw_error)
                attempts.append({
                    "model": model_name,
                    "error_code": normalized["error_code"],
                    "error": normalized["error"],
                    "raw_error": raw_error,
                })
                logger.warning(
                    "模型 %s 調用失敗，error_code=%s",
                    model_name,
                    normalized["error_code"]
                )

                # 配額/暫時不可用/模型不存在才繼續嘗試備援模型
                can_fallback = normalized["error_code"] in {
                    "quota_exceeded",
                    "service_unavailable",
                    "model_not_found",
                }
                has_next_model = index < len(self.model_candidates) - 1

                if can_fallback and has_next_model:
                    logger.info(
                        "切換備援模型: %s -> %s",
                        model_name,
                        self.model_candidates[index + 1]
                    )
                    continue

                break

        final_attempt = attempts[-1] if attempts else {
            "model": self.model_name,
            "error_code": "unknown_error",
            "error": "翻譯服務發生未知錯誤，請稍後再試。",
            "raw_error": "Unknown error"
        }

        return {
            "success": False,
            "error_code": final_attempt["error_code"],
            "error": final_attempt["error"],
            "raw_error": final_attempt["raw_error"],
            "model": final_attempt["model"],
            "fallback_used": len(attempts) > 1,
            "attempts": attempts,
        }
    
    def translate(
        self,
        text: str,
        target_language: Optional[str] = None,
        source_language: Optional[str] = None,
        custom_system_prompt: Optional[str] = None
    ) -> Dict[str, any]:
        """
        翻譯文本。
        
        此方法進行以下步驟：
        1. 驗證輸入文本
        2. 檢測源語言（如果未指定）
        3. 如果源語言等於目標語言，返回原文
        4. 調用 Gemini API 進行翻譯
        5. 驗證和返回結果
        
        Args:
            text: 要翻譯的文本
            target_language: 目標語言，預設使用配置中的值
            source_language: 源語言，若未指定則自動檢測
            custom_system_prompt: 自定義系統提示詞，若提供則使用此提示而非默認翻譯提示
            
        Returns:
            Dict[str, any]: 包含以下鍵值的字典：
                - success (bool): 翻譯是否成功
                - translation (str): 翻譯結果 (若成功)
                - source_language (str): 源語言名稱
                - target_language (str): 目標語言名稱
                - error (str): 錯誤信息 (若失敗)
                
        Example:
            >>> translator = GeminiTranslator()
            >>> result = translator.translate("Hello World", "zh-TW")
            >>> if result["success"]:
            ...     print(result["translation"])
            ... else:
            ...     print(result["error"])
        """
        # 設置預設目標語言
        if target_language is None:
            target_language = Config.get_default_target_language()
        
        # 輸入驗證
        if not text or not isinstance(text, str):
            return {
                "success": False,
                "error": "輸入文本無效"
            }
        
        text = text.strip()
        
        try:
            # 自動檢測源語言
            if source_language is None:
                detected = self.language_detector.detect_language(text)
                source_language = detected["language"]
                source_lang_name = detected["language_name"]
            else:
                source_lang_name = source_language
            
            # 轉換目標語言代碼為語言名稱
            target_lang_name = self._convert_lang_code_to_name(target_language)
            
            # 如果源語言和目標語言相同，直接返回原文
            if source_language == target_language:
                logger.info(
                    f"源語言和目標語言相同，直接返回原文"
                )
                return {
                    "success": True,
                    "translation": text,
                    "source_language": source_lang_name,
                    "target_language": target_lang_name,
                    "is_same_language": True
                }
            
            # 構建翻譯提示詞
            if custom_system_prompt:
                # 如果提供自定義系統提示，將文本附加到提示末尾
                prompt = f"{custom_system_prompt}\n\n{text}"
            else:
                # 使用默認翻譯提示詞
                prompt = self._build_translation_prompt(
                    text,
                    source_lang_name,
                    target_lang_name
                )
            
            # 調用 Gemini API（含備援模型）
            logger.debug(f"調用 Gemini API，提示: {prompt[:100]}...")

            generation = self._generate_content_with_fallback(prompt)
            if not generation["success"]:
                return {
                    "success": False,
                    "error": generation["error"],
                    "error_code": generation["error_code"],
                    "raw_error": generation["raw_error"],
                    "model": generation["model"],
                    "fallback_used": generation["fallback_used"],
                }

            response = generation["response"]
            
            if not response or not response.text:
                return {
                    "success": False,
                    "error": "Gemini API 未返回有效響應"
                }
            
            translation = response.text.strip()
            
            logger.info(
                f"翻譯成功 ({source_lang_name} → {target_lang_name})"
            )
            
            return {
                "success": True,
                "translation": translation,
                "source_language": source_lang_name,
                "target_language": target_lang_name,
                "model": generation["model"],
                "fallback_used": generation["fallback_used"],
            }
            
        except Exception as e:
            raw_error = str(e)
            normalized = _normalize_gemini_error_message(raw_error)
            logger.error(f"翻譯過程出錯: {raw_error}", exc_info=True)
            return {
                "success": False,
                "error": normalized["error"],
                "error_code": normalized["error_code"],
                "raw_error": raw_error
            }
    
    def _build_translation_prompt(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> str:
        """
        構建翻譯提示詞。
        
        此方法生成發送給 Gemini 的翻譯指令。
        
        Args:
            text: 要翻譯的文本
            source_language: 源語言名稱
            target_language: 目標語言名稱
            
        Returns:
            str: 格式化的翻譯提示詞
        """
        prompt = (
            f"請將以下 {source_language} 文本翻譯為 {target_language}。\n"
            f"只返回翻譯結果，不需要任何解釋。\n\n"
            f"原文:\n{text}"
        )
        return prompt
    
    def _convert_lang_code_to_name(self, lang_code: str) -> str:
        """
        將語言代碼轉換為語言名稱。
        
        Args:
            lang_code: 語言代碼 (e.g., "en", "zh-TW")
            
        Returns:
            str: 語言名稱
        """
        lang_map = {
            "en": "English",
            "zh": "Chinese",
            "zh-TW": "Traditional Chinese",
            "zh-CN": "Simplified Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "ru": "Russian",
        }
        return lang_map.get(lang_code, lang_code)
