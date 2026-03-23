#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整代碼示例 - LINE Bot Quick Reply 快速選單功能實現

此文件展示了三個主要組件的代碼實現細節和工作流程。
實際代碼已集成到項目的以下文件中：
- src/translator/gemini_translator.py
- src/line_bot/handler.py
- app/handler.py
- main.py
"""

# ============================================================================
# 第一部分：翻譯引擎增強 (gemini_translator.py)
# ============================================================================

"""
修改 translate() 方法簽名，支持自定義系統提示詞：

def translate(
    self,
    text: str,
    target_language: Optional[str] = None,
    source_language: Optional[str] = None,
    custom_system_prompt: Optional[str] = None
) -> Dict[str, any]:
    \"\"\"
    使用可選的自定義系統提示詞進行翻譯。
    
    Args:
        text: 要翻譯的文本
        target_language: 目標語言代碼
        source_language: 源語言代碼
        custom_system_prompt: 自定義系統提示詞
    \"\"\"
    
    # ... 設置預設目標語言 ...
    
    try:
        # ... 檢測源語言 ...
        
        # 關鍵改動：支持自定義提示詞
        if custom_system_prompt:
            # 使用自定義提示詞
            prompt = f"{custom_system_prompt}\\n\\n{text}"
        else:
            # 使用默認翻譯提示詞
            prompt = self._build_translation_prompt(
                text,
                source_lang_name,
                target_lang_name
            )
        
        # ... 調用 Gemini API ...
"""


# ============================================================================
# 第二部分：快速選單和狀態管理 (handler.py)
# ============================================================================

"""
核心函數實現：
"""

def _create_mode_selection_quick_reply():
    """
    建立翻譯模式選擇的 Quick Reply 訊息。
    
    返回包含三個按鈕的快速選單：
    - 中日翻譯：日文模式
    - 中英翻譯：英文模式
    - 中英日對照：三語模式
    """
    # QuickReply 物件語法：
    # quick_reply = QuickReply(
    #     items=[
    #         QuickReplyButton(action=MessageAction(label="按鈕標籤", text="用戶點擊時發送的文本")),
    #         ...
    #     ]
    # )
    pass


def _get_translation_system_prompt(mode: str) -> str:
    """
    根據用戶選擇的翻譯模式，返回對應的系統提示詞。
    
    Args:
        mode: "ja" (日文) | "en" (英文) | "multi" (三語)
    
    Returns:
        優化過的系統提示詞，指導 Gemini 進行特定類型的翻譯
    """
    prompts = {
        "ja": "你是一個專業的翻譯助手。請將提供的中文內容翻譯為日文。只返回日文翻譯結果，不需要任何解釋或額外說明。",
        "en": "你是一個專業的翻譯助手。請將提供的中文內容翻譯為英文。只返回英文翻譯結果，不需要任何解釋或額外說明。",
        "multi": "你是一個專業的多語言翻譯助手。請將提供的中文內容同時翻譯為英文和日文。格式為:\\n【英文翻譯】\\n[內容]\\n\\n【日文翻譯】\\n[內容]\\n\\n只返回翻譯結果，不需要解釋。"
    }
    return prompts.get(mode, prompts["ja"])


# ============================================================================
# 第三部分：消息處理流程 (handler.py)
# ============================================================================

"""
修改後的 handle_text_message() 函數流程圖：

1. 收到用戶消息
   ↓
2. 檢查是否為菜單觸發指令 ("選單" / "menu")
   ├─ 是 → 發送快速選單 QuickReply，返回
   └─ 否 → 繼續
   
3. 檢查是否為模式切換指令 ("切換為日文模式" / "切換為英文模式" / "切換為三語模式")
   ├─ 是 → 更新 user_prefs[user_id]，發送確認信息，返回
   └─ 否 → 繼續
   
4. 普通翻譯流程
   ├─ 驗證消息長度
   ├─ 從 user_prefs 獲取用戶的翻譯模式（默認 "ja"）
   ├─ 生成該模式的系統提示詞
   ├─ 調用 translator.translate(user_message, custom_system_prompt=prompt)
   ├─ 格式化回覆
   └─ 發送翻譯結果

關鍵代碼片段：

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event: MessageEvent):
    user_id = event.source.user_id
    user_message = event.message.text.strip()
    
    # 檢查菜單觸發
    if user_message.lower() in ["選單", "menu"]:
        line_bot_api.reply_message(
            event.reply_token,
            _create_mode_selection_quick_reply()
        )
        return
    
    # 檢查模式切換
    if user_message == "切換為日文模式":
        user_prefs[user_id] = "ja"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="✅ 已切換到【日文模式】")
        )
        return
    # ... 類似的 en 和 multi 分支 ...
    
    # 普通翻譯流程
    mode = user_prefs.get(user_id, "ja")
    system_prompt = _get_translation_system_prompt(mode)
    
    # 重點：傳遞自定義系統提示詞
    translation_result = translator.translate(
        user_message,
        custom_system_prompt=system_prompt
    )
    
    # ... 發送結果 ...
"""


# ============================================================================
# 第四部分：狀態管理 (app/handler.py 和 main.py)
# ============================================================================

"""
全局狀態管理結構：

在 app/handler.py 中定義：

    user_prefs = {}  # {user_id: "ja" | "en" | "multi"}

此字典的生命週期：
- 初始化：Flask 應用啟動時，user_prefs 為空 {}
- 運行時：每當用戶選擇模式時，user_prefs[user_id] 被更新
- 保存：當前存儲在內存中，服務器重啟時重置

示例場景：

    user_prefs = {
        "U1234567890": "ja",      # 用戶 1 使用日文模式
        "U9876543210": "en",      # 用戶 2 使用英文模式
        "U1111111111": "multi",   # 用戶 3 使用三語模式
    }

每個用戶的設置獨立且隔離，不會互相影響。
"""


# ============================================================================
# 第五部分：使用示例和 API 調用
# ============================================================================

"""
完整的用戶交互示例：

---
用戶 (User ID: U123456):
> 選單

Bot:
[快速選單消息，包含三個按鈕]
請選擇翻譯模式:
• 中日翻譯：將中文翻譯為日文
• 中英翻譯：將中文翻譯為英文
• 中英日對照：同時提供英文和日文翻譯

[按鈕]
├─ 中日翻譯
├─ 中英翻譯
└─ 中英日對照

用戶點擊 "中英翻譯"
↓ (系統發送: "切換為英文模式")

Bot:
✅ 已切換到【英文模式】

現在向我發送文本，我將為您翻譯。
(輸入『選單』或『menu』可重新選擇)

用戶:
> Hello, this is a test

Bot:
Original: Hello, this is a test
English: Hello, this is a test.
---

緊接著，同一用戶再次交互：

用戶:
> 選單

Bot:
[再次顯示快速選單]

用戶點擊 "中英日對照"

Bot:
✅ 已切換到【三語模式】

用戶:
> I like learning

Bot:
Original: I like learning
【English Translation】
I like learning.

【Japanese Translation】
私は学習が好きです。
"""


# ============================================================================
# 第六部分：API 参數和返回值
# ============================================================================

"""
translator.translate() 方法的新簽名：

def translate(
    self,
    text: str,
    target_language: Optional[str] = None,
    source_language: Optional[str] = None,
    custom_system_prompt: Optional[str] = None
) -> Dict[str, any]

調用示例：

# 1. 默認翻譯（如前的行為）
result = translator.translate("Hello World")
# 系統會自動檢測源語言並翻譯為預設目標語言

# 2. 指定目標語言
result = translator.translate("Hello", target_language="ja")

# 3. 使用自定義系統提示詞（新功能）
custom_prompt = "將以下文本翻譯為日文"
result = translator.translate("Hello", custom_system_prompt=custom_prompt)

返回值結構（成功時）：
{
    "success": True,
    "translation": "翻譯後的文本",
    "source_language": "English",
    "target_language": "Japanese",
    "model": "gemini-1.5-flash",
    "fallback_used": False
}

返回值結構（失敗時）：
{
    "success": False,
    "error": "用戶友好的錯誤消息",
    "error_code": "quota_exceeded" | "service_unavailable" | "unknown_error",
    "raw_error": "原始錯誤消息"
}
"""


# ============================================================================
# 第七部分：未來擴展建議
# ============================================================================

"""
1. 持久化用戶模式
   
   目前: 使用內存字典 (服務器重啟後丟失)
   升級: 使用 Redis 或 SQLite 保存用戶設置
   
   實現方式：
   - 在 handler 中初始化時從 Redis 加載 user_prefs
   - 每次更新時同時更新 Redis
   
2. 更多翻譯模式
   
   當前: 3 種模式 (日文、英文、三語)
   未來: 支持 6+ 種語言組合
   
   實現方式：
   - 擴展 _get_translation_system_prompt()
   - 修改 _create_mode_selection_quick_reply() 的按鈕數量
   
3. 用戶偏好應用
   
   當前: 只在翻譯時應用
   未來: 應用到其他功能（如語言檢測偏好、格式化偏好等）
   
4. 分析和統計
   
   - 記錄用戶選擇歷史
   - 分析最受歡迎的翻譯模式
   - 推送定性反饋

5. 智能推薦
   
   - 根據用戶歷史自動推薦常用模式
   - A/B 測試不同的 UI 設計
"""
