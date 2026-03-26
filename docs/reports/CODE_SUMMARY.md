#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
==============================================================================
LINE Bot Quick Reply 快速選單功能 - 完整代碼實現總結
==============================================================================

本文件提供了所有修改的完整代碼片段，便於查閱和部署。

修改的文件：
1. src/translator/gemini_translator.py
2. src/line_bot/handler.py  
3. app/handler.py
4. main.py (文檔更新)
==============================================================================
"""

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ 文件 1: src/translator/gemini_translator.py
# ║ 修改: 添加自定義系統提示詞支持
# ╚══════════════════════════════════════════════════════════════════════════╝

"""
修改1: 更新 translate() 方法簽名
---
位置: gemini_translator.py 的 translate() 方法

舊簽名:
    def translate(
        self,
        text: str,
        target_language: Optional[str] = None,
        source_language: Optional[str] = None
    ) -> Dict[str, any]:

新簽名:
    def translate(
        self,
        text: str,
        target_language: Optional[str] = None,
        source_language: Optional[str] = None,
        custom_system_prompt: Optional[str] = None
    ) -> Dict[str, any]:

---
修改2: 更新方法文檔
---
在 translate() 的 docstring 中添加新參數說明：
    
    Args:
        ...既有參數...
        custom_system_prompt: 自定義系統提示詞，若提供則使用此提示而非默認翻譯提示

---
修改3: 修改 Prompt 構建邏輯
---
位置: translate() 方法內，約在第 240-250 行

舊代碼:
    # 構建翻譯提示詞
    prompt = self._build_translation_prompt(
        text,
        source_lang_name,
        target_lang_name
    )

新代碼:
    # 構建翻譯提示詞
    if custom_system_prompt:
        # 如果提供自定義系統提示，將文本附加到提示末尾
        prompt = f"{custom_system_prompt}\\n\\n{text}"
    else:
        # 使用默認翻譯提示詞
        prompt = self._build_translation_prompt(
            text,
            source_lang_name,
            target_lang_name
        )
"""


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ 文件 2: src/line_bot/handler.py
# ║ 修改: 添加 Quick Reply 菜單和模式切換邏輯
# ╚══════════════════════════════════════════════════════════════════════════╝

"""
修改1: 更新導入
---
舊導入:
    import logging
    from flask import Blueprint, request, abort
    from linebot import LineBotApi, WebhookHandler
    from linebot.exceptions import InvalidSignatureError
    from linebot.models.events import MessageEvent
    from linebot.models.messages import TextMessage
    from linebot.models.send_messages import TextSendMessage

新導入:
    import logging
    from flask import Blueprint, request, abort
    from linebot import LineBotApi, WebhookHandler
    from linebot.exceptions import InvalidSignatureError
    from linebot.models.events import MessageEvent
    from linebot.models.messages import TextMessage
    from linebot.models.send_messages import TextSendMessage
    from linebot.models.quick_reply import QuickReply, QuickReplyButton
    from linebot.models.template import ButtonsTemplate
    from linebot.models.action import MessageAction

---
修改2: 添加輔助函數 _create_mode_selection_quick_reply()
---
位置: _build_user_error_message() 函數之後

代碼:
    def _create_mode_selection_quick_reply() -> dict:
        \"\"\"
        建立翻譯模式選擇的 Quick Reply 訊息。
        \"\"\"
        quick_reply = QuickReply(
            items=[
                QuickReplyButton(
                    action=MessageAction(
                        label="中日翻譯",
                        text="切換為日文模式"
                    )
                ),
                QuickReplyButton(
                    action=MessageAction(
                        label="中英翻譯",
                        text="切換為英文模式"
                    )
                ),
                QuickReplyButton(
                    action=MessageAction(
                        label="中英日對照",
                        text="切換為三語模式"
                    )
                ),
            ]
        )
        
        message = TextSendMessage(
            text="請選擇翻譯模式:\\n\\n• 中日翻譯：將中文翻譯為日文\\n• 中英翻譯：將中文翻譯為英文\\n• 中英日對照：同時提供英文和日文翻譯",
            quick_reply=quick_reply
        )
        
        return message

---
修改3: 添加輔助函數 _get_translation_system_prompt()
---
位置: _create_mode_selection_quick_reply() 函數之後

代碼:
    def _get_translation_system_prompt(mode: str) -> str:
        \"\"\"
        根據翻譯模式返回相應的系統提示詞。
        \"\"\"
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
                "格式為:\\n"
                "【英文翻譯】\\n[英文內容]\\n\\n"
                "【日文翻譯】\\n[日文內容]\\n\\n"
                "只返回翻譯結果，不需要任何解釋。"
            )
        else:
            return (
                "你是一個專業的翻譯助手。"
                "請將提供的中文內容翻譯為日文。"
                "只返回日文翻譯結果，不需要任何解釋或額外說明。"
            )

---
修改4: 更新 create_line_bot_handler() 函數簽名
---
舊簽名:
    def create_line_bot_handler() -> Blueprint:

新簽名:
    def create_line_bot_handler(user_prefs: dict) -> Blueprint:

---
修改5: 完全重新實現 handle_text_message() 函數
---
位置: @handler.add 裝飾器下的函數

完整代碼見下面的代碼塊...
"""


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ 完整的 handle_text_message() 函數實現
# ╚══════════════════════════════════════════════════════════════════════════╝

"""
    @handler.add(MessageEvent, message=TextMessage)
    def handle_text_message(event: MessageEvent):
        \"\"\"
        處理文字消息事件。
        \"\"\"
        try:
            user_id = event.source.user_id
            user_message = event.message.text.strip()
            
            logger.info(f"收到來自 {user_id} 的消息: {user_message}")
            
            # ========== 1. 檢查菜單觸發指令 ==========
            if user_message.lower() in ["選單", "menu"]:
                try:
                    line_bot_api.reply_message(
                        event.reply_token,
                        _create_mode_selection_quick_reply()
                    )
                    logger.info(f"已向 {user_id} 發送模式選擇菜單")
                except Exception as menu_err:
                    logger.error(f"發送菜單失敗: {str(menu_err)}")
                return
            
            # ========== 2. 檢查模式切換指令 ==========
            if user_message in ["切換為日文模式", "切換為英文模式", "切換為三語模式"]:
                if user_message == "切換為日文模式":
                    user_prefs[user_id] = "ja"
                    mode_name = "日文"
                elif user_message == "切換為英文模式":
                    user_prefs[user_id] = "en"
                    mode_name = "英文"
                else:  # "切換為三語模式"
                    user_prefs[user_id] = "multi"
                    mode_name = "三語"
                
                try:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text=f"✅ 已切換到【{mode_name}模式】\\n\\n"
                                 f"現在向我發送文本，我將為您翻譯。\\n"
                                 f"(輸入『選單』或『menu』可重新選擇)"
                        )
                    )
                    logger.info(f"用戶 {user_id} 已切換到 {mode_name} 模式")
                except Exception as switch_err:
                    logger.error(f"發送模式切換確認失敗: {str(switch_err)}")
                return
            
            # ========== 3. 普通翻譯流程 ==========
            # 驗證消息長度
            if not validate_message_length(user_message):
                error_msg = (
                    f"消息過長，最多支持 {Config.get_max_message_length()} 個字符。"
                )
                try:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=error_msg)
                    )
                except Exception as reply_err:
                    logger.error(f"發送長度限制錯誤消息失敗: {str(reply_err)}")
                logger.warning(f"消息超過長度限制: {user_id}")
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
"""


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ 文件 3: app/handler.py
# ║ 修改: 添加全局狀態管理和傳遞給 create_line_bot_handler()
# ╚══════════════════════════════════════════════════════════════════════════╝

"""
完整的 app/handler.py 代碼:

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

\"\"\"App handler module exposing the webhook blueprint.\"\"\"

from src.line_bot.handler import create_line_bot_handler

# 全局用戶偏好設置字典
# 結構: {user_id: "ja" | "en" | "multi"}
user_prefs = {}


def line_webhook_bp():
    \"\"\"Lazily create and return the LINE webhook blueprint.\"\"\"
    return create_line_bot_handler(user_prefs)
"""


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ 文件 4: main.py
# ║ 修改: 更新文檔說明狀態管理
# ╚══════════════════════════════════════════════════════════════════════════╝

"""
在 main.py 的 docstring 中添加以下內容:

狀態管理:
---------
此應用使用全局 user_prefs 字典管理用戶的翻譯模式设置：
- 鍵: user_id (LINE 用戶 ID)
- 值: "ja" (日文) | "en" (英文) | "multi" (中英日對照)
- 默認值: "ja" (日文模式)

快速選單功能:
-----------
- 用戶輸入 "選單" 或 "menu" 返回翻譯模式選擇菜單
- 用戶選擇後，user_prefs 被更新
- 後續翻譯將根據選擇的模式使用不同的 Prompt
"""


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ 關鍵改動對比
# ╚══════════════════════════════════════════════════════════════════════════╝

"""
┌─ 翻譯流程對比 ─────────────────────────────────────────────────────────┐
│                                                                          │
│ 舊流程:                    │ 新流程:                                   │
│ ═══════════════════════════╪═════════════════════════════════════════  │
│ 用戶發送文本               │ 用戶輸入「選單」或「menu」                 │
│ ↓                          │ ↓                                          │
│ 檢測語言                   │ 顯示 Quick Reply 選單                      │
│ ↓                          │ ↓                                          │
│ 使用默認提示詞翻譯          │ 用戶點擊選擇模式                           │
│ ↓                          │ ↓                                          │
│ 返回翻譯結果               │ 保存模式到 user_prefs[user_id]             │
│                            │ ↓                                          │
│                            │ 用戶發送文本                                │
│                            │ ↓                                          │
│                            │ 檢測語言                                    │
│                            │ ↓                                          │
│                            │ 根據 user_prefs[user_id] 選擇提示詞        │
│                            │ ↓                                          │
│                            │ 翻譯                                        │
│                            │ ↓                                          │
│                            │ 返回翻譯結果                                │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
"""


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ 部署檢查清單
# ╚══════════════════════════════════════════════════════════════════════════╝

"""
□ 修改了 src/translator/gemini_translator.py
  - translate() 方法簽名已更新，支持 custom_system_prompt 參數
  - Prompt 構建邏輯已修改，支持自定義提示詞

□ 修改了 src/line_bot/handler.py
  - 導入了 QuickReply 相關類
  - 添加了 _create_mode_selection_quick_reply() 函數
  - 添加了 _get_translation_system_prompt() 函數
  - 修改了 create_line_bot_handler() 函數簽名
  - 重新實現了 handle_text_message() 函數

□ 修改了 app/handler.py
  - 定義了全局 user_prefs 字典
  - 傳遞 user_prefs 給 create_line_bot_handler()

□ 更新了 main.py 文檔
  - 添加了狀態管理的說明

□ 測試代碼
  - 已創建 test_quick_reply.py 包含單元測試和集成測試

□ 文檔
  - 已創建 QUICK_REPLY_GUIDE.md - 使用指南
  - 已創建 IMPLEMENTATION_DETAILS.md - 實現細節

□ 程序運行
  python main.py

□ 訪問 health 檢查端點
  curl http://localhost:5000/health
  應返回: OK 200

□ 配置 LINE Bot webhook URL
  輸入: https://your-server/line/webhook

□ 在 LINE 上測試
  1. 輸入「選單」或「menu」
  2. 點擊按鈕選擇翻譯模式
  3. 發送中文文本進行翻譯
  4. 重複步驟 1-3 測試不同模式
"""
