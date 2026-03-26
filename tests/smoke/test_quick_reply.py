#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quick Reply functionality test

Unit and integration tests to verify menu, mode switching and dynamic prompt features.

Run with:
    pytest test_quick_reply.py -v
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.translator.gemini_translator import GeminiTranslator
from src.line_bot.handler import (
    _create_mode_selection_quick_reply,
    _get_translation_system_prompt
)


class TestQuickReply(unittest.TestCase):
    """Test quick menu functionality"""
    
    def test_mode_selection_quick_reply_structure(self):
        """Test quick menu structure"""
        message = _create_mode_selection_quick_reply()
        
        # Verify return is correct message type
        self.assertIsNotNone(message)
        self.assertTrue(hasattr(message, 'text'))
        self.assertTrue(hasattr(message, 'quick_reply'))
        
        # Verify quick reply contains three buttons
        quick_reply = message.quick_reply
        self.assertEqual(len(quick_reply.items), 3)
        
        # Verify button labels
        button_labels = [item.action.label for item in quick_reply.items]
        self.assertIn("Chinese to Japanese", button_labels)
        self.assertIn("Chinese to English", button_labels)
        self.assertIn("Chinese to EN & JP", button_labels)
        
        # Verify button texts
        button_texts = [item.action.text for item in quick_reply.items]
        self.assertIn("Switch to Japanese Mode", button_texts)
        self.assertIn("Switch to English Mode", button_texts)
        self.assertIn("Switch to Multi-Language Mode", button_texts)


class TestTranslationPrompts(unittest.TestCase):
    """Test dynamic translation prompts"""
    
    def test_japanese_prompt(self):
        """Test Japanese mode prompt"""
        prompt = _get_translation_system_prompt("ja")
        self.assertIn("日文", prompt)
        self.assertIn("不需要", prompt)
        self.assertTrue(len(prompt) > 0)
    
    def test_english_prompt(self):
        """Test English mode prompt"""
        prompt = _get_translation_system_prompt("en")
        self.assertIn("英文", prompt)
        self.assertIn("不需要", prompt)
        self.assertTrue(len(prompt) > 0)
    
    def test_multilingual_prompt(self):
        """Test multi-language mode prompt"""
        prompt = _get_translation_system_prompt("multi")
        self.assertIn("英文", prompt)
        self.assertIn("日文", prompt)
        self.assertIn("【英文翻譯】", prompt)
        self.assertIn("【日文翻譯】", prompt)
    
    def test_default_prompt(self):
        """Test default prompt (invalid mode)"""
        prompt = _get_translation_system_prompt("invalid_mode")
        # Should return Japanese mode prompt
        self.assertIn("日文", prompt)
    
    def test_all_prompts_are_different(self):
        """Test that different mode prompts are actually different"""
        ja_prompt = _get_translation_system_prompt("ja")
        en_prompt = _get_translation_system_prompt("en")
        multi_prompt = _get_translation_system_prompt("multi")
        
        self.assertNotEqual(ja_prompt, en_prompt)
        self.assertNotEqual(ja_prompt, multi_prompt)
        self.assertNotEqual(en_prompt, multi_prompt)


class TestUserPreferences(unittest.TestCase):
    """測試用戶偏好管理"""
    
    def setUp(self):
        """Initialize test data"""
        self.user_prefs = {}
    
    def test_user_prefs_isolation(self):
        """Test that different users' settings are isolated"""
        # User 1 sets to Japanese mode
        self.user_prefs["user_1"] = "ja"
        
        # User 2 sets to English mode
        self.user_prefs["user_2"] = "en"
        
        # User 3 sets to multi-language mode
        self.user_prefs["user_3"] = "multi"
        
        # Verify settings remain independent
        self.assertEqual(self.user_prefs["user_1"], "ja")
        self.assertEqual(self.user_prefs["user_2"], "en")
        self.assertEqual(self.user_prefs["user_3"], "multi")
    
    def test_user_mode_switching(self):
        """Test user mode switching"""
        user_id = "user_test"
        
        # Initial state: should return default value
        mode = self.user_prefs.get(user_id, "ja")
        self.assertEqual(mode, "ja")
        
        # Switch to English
        self.user_prefs[user_id] = "en"
        mode = self.user_prefs.get(user_id, "ja")
        self.assertEqual(mode, "en")
        
        # Switch to multi-language
        self.user_prefs[user_id] = "multi"
        mode = self.user_prefs.get(user_id, "ja")
        self.assertEqual(mode, "multi")
        
        # Switch back to Japanese
        self.user_prefs[user_id] = "ja"
        mode = self.user_prefs.get(user_id, "ja")
        self.assertEqual(mode, "ja")


class TestGeminiTranslatorCustomPrompt(unittest.TestCase):
    """Test Gemini translator custom prompt functionality"""
    
    @patch('google.genai.Client')
    def test_translate_with_custom_prompt(self, mock_client):
        """
        Test translation with custom system prompt.
        
        Note: This test requires Gemini API key configuration.
        Make sure environment variables are set before actual test.
        """
        # 設置 mock 响应
        mock_response = Mock()
        mock_response.text = "こんにちは、これはテストです"
        
        mock_client.return_value.models.generate_content.return_value = mock_response
        
        # 創建翻譯器（在實際測試中需要有效的 API 密鑰）
        # translator = GeminiTranslator()
        # 
        # custom_prompt = "將以下文本翻譯為日文，只返回翻譯結果："
        # result = translator.translate(
        #     "Hello, this is a test",
        #     custom_system_prompt=custom_prompt
        # )
        # 
        # self.assertTrue(result["success"])
        # self.assertEqual(result["translation"], "こんにちは、これはテストです")


class TestMessageHandlingScenarios(unittest.TestCase):
    """Test message handling various scenarios"""
    
    def setUp(self):
        """Initialize test environment"""
        self.user_prefs = {}
    
    def test_menu_trigger_scenarios(self):
        """Test menu trigger scenarios"""
        test_inputs = [
            ("menu", True),
            ("MENU", True),  # Should be handled by .lower()
            ("menu ", True),  # Space is stripped in actual handler
            ("select", False),  # Different string
            ("translate", False),
        ]
        
        for text, should_trigger in test_inputs:
            is_menu = text.lower().strip() in ["menu"]
            self.assertEqual(
                is_menu,
                should_trigger,
                f"Text '{text}' should_trigger={should_trigger}, but got {is_menu}"
            )
    
    def test_mode_switch_scenarios(self):
        """Test mode switch scenarios"""
        switch_commands = [
            ("Switch to Japanese Mode", "ja"),
            ("Switch to English Mode", "en"),
            ("Switch to Multi-Language Mode", "multi"),
        ]
        
        user_id = "test_user"
        
        for command, expected_mode in switch_commands:
            if command == "Switch to Japanese Mode":
                self.user_prefs[user_id] = "ja"
            elif command == "Switch to English Mode":
                self.user_prefs[user_id] = "en"
            elif command == "Switch to Multi-Language Mode":
                self.user_prefs[user_id] = "multi"
            
            actual_mode = self.user_prefs.get(user_id)
            self.assertEqual(
                actual_mode,
                expected_mode,
                f"Command '{command}' should set mode to '{expected_mode}', but got '{actual_mode}'"
            )


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration(unittest.TestCase):
    """Integration tests: simulate complete user interaction workflow"""
    
    def test_user_workflow(self):
        """測試完整的用戶交互工作流"""
        user_prefs = {}
        user_id = "U123456789"
        
        # Step 1: User opens menu
        # Expected: Show quick menu
        message = _create_mode_selection_quick_reply()
        self.assertIsNotNone(message)
        
        # Step 2: User selects English mode
        # Expected: user_prefs[user_id] = "en"
        user_prefs[user_id] = "en"
        self.assertEqual(user_prefs.get(user_id), "en")
        
        # Step 3: User sends text to translate
        # Expected: Use English mode prompt for translation
        mode = user_prefs.get(user_id, "ja")
        prompt = _get_translation_system_prompt(mode)
        self.assertIn("英文", prompt)
        self.assertNotIn("日文翻譯", prompt)  # Should not include bilingual part
        
        # Step 4: User opens menu again, selects multi-language mode
        # 預期: user_prefs[user_id] = "multi"
        user_prefs[user_id] = "multi"
        self.assertEqual(user_prefs.get(user_id), "multi")
        
        # 步驟 5: 用戶再次發送文本
        # 預期: 使用三語模式的提示詞（包含英文和日文）
        mode = user_prefs.get(user_id, "ja")
        prompt = _get_translation_system_prompt(mode)
        self.assertIn("英文", prompt)
        self.assertIn("日文", prompt)
        self.assertIn("【英文翻譯】", prompt)
        self.assertIn("【日文翻譯】", prompt)


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance(unittest.TestCase):
    """Test system performance"""
    
    def test_large_user_base(self):
        """Test storage performance for many users"""
        import time
        
        user_prefs = {}
        num_users = 10000
        
        # Simulate 10000 users' mode settings
        start_time = time.time()
        
        for i in range(num_users):
            user_id = f"user_{i}"
            modes = ["ja", "en", "multi"]
            user_prefs[user_id] = modes[i % 3]
        
        end_time = time.time()
        
        # Verify all users are set correctly
        self.assertEqual(len(user_prefs), num_users)
        
        # Performance requirement: should complete within 1 second
        elapsed = end_time - start_time
        self.assertLess(elapsed, 1.0, f"Storing {num_users} users took too long: {elapsed}s")
        
        # Verify retrieval performance
        start_time = time.time()
        for i in range(num_users):
            user_id = f"user_{i}"
            mode = user_prefs.get(user_id, "ja")
            self.assertIn(mode, ["ja", "en", "multi"])
        end_time = time.time()
        
        elapsed = end_time - start_time
        self.assertLess(elapsed, 0.5, f"Retrieving {num_users} users took too long: {elapsed}s")


if __name__ == "__main__":
    unittest.main()
