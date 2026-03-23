#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LINE Bot 事件處理模組

此模組負責處理 LINE Messaging API 事件，包括：
- 接收和驗證來自 LINE 的 Webhook 請求
- 解析用戶消息
- 調用翻譯服務
- 發送回覆消息

遵循模組化設計，所有翻譯邏輯都通過 translator 模組求解。
"""

import logging
from flask import Blueprint, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models.events import MessageEvent
from linebot.models.messages import TextMessage
from linebot.models.send_messages import TextSendMessage, QuickReply, QuickReplyButton
from linebot.models.template import ButtonsTemplate
from linebot.models import MessageAction

from src.config import Config
from src.translator.gemini_translator import GeminiTranslator
from src.line_bot.utils import (
    format_translation_message,
    extract_language_code,
    validate_message_length
)

# 配置日誌
logger = logging.getLogger(__name__)


def _build_user_error_message(translation_result: dict) -> str:
    """建立給 LINE 使用者的精簡錯誤訊息。"""
    error_code = translation_result.get("error_code", "unknown_error")
    fallback_used = translation_result.get("fallback_used", False)

    if error_code == "quota_exceeded":
        message = "翻譯服務目前配額不足，請稍後再試。"
    elif error_code == "service_unavailable":
        message = "翻譯服務暫時忙碌，請稍後再試。"
    elif error_code == "model_not_found":
        message = "翻譯模型暫時不可用，請稍後再試。"
    else:
        message = "翻譯暫時失敗，請稍後再試。"

    if fallback_used:
        message += "（已嘗試備援模型）"

    return message


def _create_mode_selection_quick_reply() -> dict:
    """
    建立翻譯模式選擇的 Quick Reply 訊息。
    
    Returns:
        dict: 包含 TextSendMessage 和 QuickReply 的訊息物件
    """
    quick_reply = QuickReply(
        items=[
            QuickReplyButton(
                action=MessageAction(
                    label="Chinese to Japanese",
                    text="Switch to Japanese Mode"
                )
            ),
            QuickReplyButton(
                action=MessageAction(
                    label="Chinese to English",
                    text="Switch to English Mode"
                )
            ),
            QuickReplyButton(
                action=MessageAction(
                    label="Chinese to EN & JP",
                    text="Switch to Multi-Language Mode"
                )
            ),
        ]
    )
    
    message = TextSendMessage(
        text="Select translation mode:\n\n• Chinese to Japanese\n• Chinese to English\n• Chinese to EN & JP (bilingual)",
        quick_reply=quick_reply
    )
    
    return message


def _get_translation_system_prompt(mode: str) -> str:
    """
    根據翻譯模式返回相應的系統提示詞。
    
    Args:
        mode: 翻譯模式 ('ja', 'en', 'multi')
        
    Returns:
        str: 系統提示詞
    """
    if mode == "ja":
        return (
            "你是一個專業的翻譯助手。"
            "請將提供的中文內容翻譯為日文。"
            "只返回日文翻譯結果，不需要任何解釋或額外說明。"
        )
    elif mode == "en":
        return (
            "你是一個專業的翻譯助手。"
            "請將提供的中文內容翻譯為英文。"
            "只返回英文翻譯結果，不需要任何解釋或額外說明。"
        )
    elif mode == "multi":
        return (
            "你是一個專業的多語言翻譯助手。"
            "請將提供的中文內容同時翻譯為英文和日文。"
            "格式為:\n"
            "【英文翻譯】\n[英文內容]\n\n"
            "【日文翻譯】\n[日文內容]\n\n"
            "只返回翻譯結果，不需要任何解釋。"
        )
    else:
        # 默認為日文模式
        return (
            "你是一個專業的翻譯助手。"
            "請將提供的中文內容翻譯為日文。"
            "只返回日文翻譯結果，不需要任何解釋或額外說明。"
        )


def create_line_bot_handler(user_prefs: dict) -> Blueprint:
    """
    創建 LINE Bot 事件處理 Blueprint。
    
    Returns:
        Blueprint: Flask Blueprint 實例，包含所有 LINE Bot 路由
        
    Raises:
        ValueError: 缺少必要的配置時拋出異常
    """
    # 驗證配置
    line_token = Config.get_line_channel_access_token()
    line_secret = Config.get_line_channel_secret()
    
    if not line_token or not line_secret:
        raise ValueError("缺少 LINE Channel 配置")
    
    # 創建 Blueprint
    bp = Blueprint("line_bot", __name__, url_prefix="/line")
    
    # 初始化 LINE Bot API
    line_bot_api = LineBotApi(line_token)
    handler = WebhookHandler(line_secret)
    
    # 初始化翻譯服務（無需指定 model_name，會自動從 Config 讀取）
    translator = GeminiTranslator()
    
    @bp.route("/webhook", methods=["POST"])
    def webhook():
        """
        LINE Webhook 接收端點。
        
        處理 LINE 平台發送的所有事件，包括消息事件、
        加入/離開事件等。
        
        Returns:
            tuple: (204 No Content, HTTP 204)
            
        Raises:
            abort(400): 當簽名驗證失敗時返回 400 Bad Request
        """
        signature = request.headers.get("X-Line-Signature", "")
        body = request.get_data(as_text=True)
        
        try:
            # 驗證 LINE Webhook 簽名
            handler.handle(body, signature)
        except InvalidSignatureError:
            logger.warning("接收到無效簽名的 Webhook 請求")
            abort(400)
        except Exception as e:
            logger.error(f"Webhook 處理出錯: {str(e)}", exc_info=True)
            # 不要拋出異常，直接返回 204 避免 502
            return "", 204
        
        return "", 204
    
    @handler.add(MessageEvent, message=TextMessage)
    def handle_text_message(event: MessageEvent):
        """
        處理文字消息事件。
        
        此函數執行以下流程：
        1. 提取文字內容
        2. 檢查是否觸發菜單或模式切換
        3. 驗證消息長度
        4. 檢測原始語言
        5. 調用翻譯服務
        6. 格式化並發送回覆
        
        Args:
            event: LINE TextMessageEvent 事件對象
            
        Returns:
            None
        """
        try:
            user_id = event.source.user_id
            user_message = event.message.text.strip()
            
            logger.info(f"收到來自 {user_id} 的消息: {user_message}")
            
            # ========== 1. Check for menu trigger command ==========
            if user_message.lower() in ["menu"]:
                try:
                    line_bot_api.reply_message(
                        event.reply_token,
                        _create_mode_selection_quick_reply()
                    )
                    logger.info(f"Mode selection menu sent to {user_id}")
                except Exception as menu_err:
                    logger.error(f"Error sending menu: {str(menu_err)}")
                return
            
            # ========== 2. Check for mode switch command ==========
            if user_message in ["Switch to Japanese Mode", "Switch to English Mode", "Switch to Multi-Language Mode"]:
                if user_message == "Switch to Japanese Mode":
                    user_prefs[user_id] = "ja"
                    mode_name = "Japanese"
                elif user_message == "Switch to English Mode":
                    user_prefs[user_id] = "en"
                    mode_name = "English"
                else:  # "Switch to Multi-Language Mode"
                    user_prefs[user_id] = "multi"
                    mode_name = "Multi-Language"
                
                try:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text=f"✅ Switched to {mode_name} mode\n\n"
                                 f"Send text now, I will translate it for you.\n"
                                 f"(Type 'menu' to switch modes)"
                        )
                    )
                    logger.info(f"User {user_id} switched to {mode_name} mode")
                except Exception as switch_err:
                    logger.error(f"Error sending mode switch confirmation: {str(switch_err)}")
                return
            
            # ========== 3. Regular translation flow ==========
            # Validate message length
            if not validate_message_length(user_message):
                error_msg = (
                    f"Message too long. Maximum {Config.get_max_message_length()} characters."
                )
                try:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=error_msg)
                    )
                except Exception as reply_err:
                    logger.error(f"Error sending message length error: {str(reply_err)}")
                logger.warning(f"Message exceeded length limit: {user_id}")
                return
            
            # 獲取用戶的翻譯模式（默認為 'ja'）
            mode = user_prefs.get(user_id, "ja")
            system_prompt = _get_translation_system_prompt(mode)
            
            # 調用翻譯服務（傳遞自定義系統提示詞）
            translation_result = translator.translate(
                user_message,
                custom_system_prompt=system_prompt
            )
            
            if not translation_result["success"]:
                raw_error = translation_result.get(
                    "raw_error",
                    translation_result.get("error", "Unknown")
                )
                error_msg = _build_user_error_message(translation_result)
                print(f"DEBUG Error: {raw_error}")

                try:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=error_msg)
                    )
                except Exception as reply_err:
                    logger.error(f"發送翻譯錯誤消息失敗: {str(reply_err)}")
                logger.error(
                    f"翻譯過程出錯: {raw_error} "
                    f"(error_code={translation_result.get('error_code', 'unknown_error')}, "
                    f"model={translation_result.get('model', 'unknown')}, "
                    f"fallback_used={translation_result.get('fallback_used', False)})"
                )
                return
            
            # 格式化回覆消息
            reply_text = format_translation_message(
                original_text=user_message,
                translation=translation_result["translation"],
                source_lang=translation_result.get("source_language", "unknown"),
                target_lang=translation_result.get("target_language", "unknown")
            )
            
            # 發送回覆
            try:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=reply_text)
                )
                logger.info(f"已向 {user_id} 發送翻譯結果（模式: {mode}）")
            except Exception as reply_err:
                logger.error(f"發送翻譯結果失敗: {str(reply_err)}")
            
        except Exception as e:
            logger.error(f"處理消息時發生異常: {str(e)}", exc_info=True)
            print(f"DEBUG Error: {e}")
            try:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="翻譯暫時失敗，請稍後再試。")
                )
            except Exception as final_err:
                logger.error(f"發送最終錯誤消息失敗: {str(final_err)}")
    
    return bp
