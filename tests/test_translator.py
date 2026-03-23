#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
翻譯模組單元測試

此文件包含 GeminiTranslator 和 LanguageDetector 的測試用例。

測試流程：
    pytest tests/test_translator.py

覆蓋測試項目：
    - 語言檢測功能
    - 翻譯函數
    - 錯誤處理
    - 邊界情況
"""

import pytest
from unittest.mock import patch, MagicMock
from src.translator.language_detector import LanguageDetector
from src.translator.gemini_translator import GeminiTranslator


class TestLanguageDetector:
    """LanguageDetector 類的測試套件。"""

    @pytest.fixture
    def detector(self):
        """創建 LanguageDetector 實例。"""
        return LanguageDetector()

    def test_detect_english(self, detector):
        """測試英文檢測。"""
        result = detector.detect_language("Hello World")
        assert result["language"] == "en"
        assert result["language_name"] == "English"

    def test_detect_chinese(self, detector):
        """測試中文檢測。"""
        result = detector.detect_language("你好世界")
        # 中文檢測可能返回 zh-cn 或 zh-tw
        assert "zh" in result["language"]

    def test_detect_empty_string(self, detector):
        """測試空字符串處理。"""
        result = detector.detect_language("")
        assert result["language"] == "en"  # 應該返回預設值

    def test_detect_none(self, detector):
        """測試 None 輸入處理。"""
        result = detector.detect_language(None)
        assert result["language"] == "en"

    def test_normalize_language_code(self, detector):
        """測試語言代碼標準化。"""
        assert detector._normalize_language_code("zh-CN") == "zh-cn"
        assert detector._normalize_language_code("zh-HANS") == "zh-cn"
        assert detector._normalize_language_code("en") == "en"

    def test_get_supported_languages(self, detector):
        """測試取得支持的語言列表。"""
        langs = detector.get_supported_languages()
        assert isinstance(langs, dict)
        assert "en" in langs
        assert langs["en"] == "English"

    def test_is_language_supported(self, detector):
        """測試語言支持檢查。"""
        assert detector.is_language_supported("en") is True
        assert detector.is_language_supported("zh-cn") is True
        assert detector.is_language_supported("unknown_lang") is False


class TestGeminiTranslator:
    """GeminiTranslator 類的測試套件。"""

    @pytest.fixture
    def translator(self):
        """創建 GeminiTranslator 實例（使用測試配置）。"""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("google.generativeai.configure"):
                translator = GeminiTranslator(api_key="test-key")
                return translator

    def test_translator_init_without_api_key(self):
        """測試沒有 API 密鑰時的初始化失敗。"""
        with patch.dict("os.environ", {"GEMINI_API_KEY": ""}):
            with pytest.raises(ValueError):
                GeminiTranslator(api_key="")

    def test_translator_init_with_api_key(self):
        """測試帶有 API 密鑰的初始化。"""
        with patch("google.generativeai.configure"):
            translator = GeminiTranslator(api_key="test-key")
            assert translator.api_key == "test-key"
            assert translator.model_name == "gemini-1.5-flash"

    def test_translate_empty_text(self, translator):
        """測試空文本翻譯。"""
        result = translator.translate("")
        assert result["success"] is False
        assert "error" in result

    def test_translate_none_text(self, translator):
        """測試 None 文本翻譯。"""
        result = translator.translate(None)
        assert result["success"] is False

    def test_build_translation_prompt(self, translator):
        """測試翻譯提示詞構建。"""
        prompt = translator._build_translation_prompt(
            "Hello",
            "English",
            "Traditional Chinese"
        )
        assert "Hello" in prompt
        assert "English" in prompt
        assert "Traditional Chinese" in prompt

    def test_convert_lang_code_to_name(self, translator):
        """測試語言代碼轉換。"""
        assert translator._convert_lang_code_to_name("en") == "English"
        assert translator._convert_lang_code_to_name("zh-TW") == "Traditional Chinese"
        assert translator._convert_lang_code_to_name("unknown") == "unknown"

    @patch("google.generativeai.GenerativeModel")
    def test_translate_success(self, mock_model, translator):
        """測試成功的翻譯操作。"""
        # 模擬 Gemini API 響應
        mock_response = MagicMock()
        mock_response.text = "你好"
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_instance

        result = translator.translate("Hello", target_language="zh-TW")

        assert result["success"] is True
        assert "translation" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
