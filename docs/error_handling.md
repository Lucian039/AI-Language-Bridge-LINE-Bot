# 錯誤處理文檔

## 概述

AI Language Bridge 項目採用全面的錯誤處理機制，確保應用的穩定性和可維護性。

## 錯誤分類

### 1. 配置錯誤

**場景**：缺少必要的環境變數

```python
# main.py 中的驗證
required_vars = [
    "LINE_CHANNEL_ACCESS_TOKEN",
    "LINE_CHANNEL_SECRET",
    "GEMINI_API_KEY"
]

if missing:
    raise ValueError(f"缺少必要的環境變數: {', '.join(missing)}")
```

**解決方案**：
1. 檢查 `.env` 文件是否存在
2. 驗證所有必要的密鑰已填入
3. 檢查密鑰格式是否正確

### 2. LINE Webhook 錯誤

#### InvalidSignatureError

**原因**：
- X-Line-Signature 與預期簽名不匹配
- 可能是中間人攻擊或配置錯誤

```python
@bp.route("/line/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.warning("接收到無效簽名的 Webhook 請求")
        abort(400)
```

**恢復措施**：
- 記錄警告日誌
- 返回 HTTP 400 Bad Request
- 檢查 LINE_CHANNEL_SECRET 是否正確

#### 消息驗證錯誤

**場景**：消息長度超過限制

```python
if not validate_message_length(user_message):
    error_msg = f"消息過長，最多支持 {Config.MAX_MESSAGE_LENGTH} 個字符。"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=error_msg)
    )
```

**返回信息**：用戶友好的錯誤信息，而不是技術細節

### 3. 翻譯服務錯誤

#### Language Detection 失敗

**原因**：
- 文本過短
- 文本含有特殊字符或非字母內容
- langdetect 內部錯誤

**處理方式**：
```python
def detect_language(self, text: str) -> Dict[str, str]:
    try:
        detected_code = detect(text)
        # ... 處理
    except LangDetectException as e:
        logger.warning(f"語言檢測失敗: {str(e)}，使用預設值")
        return {
            "language": "en",
            "language_name": "English",
            "confidence": "檢測失敗，使用預設"
        }
```

**恢復策略**：
- 使用預設語言（English）
- 記錄警告日誌
- 繼續翻譯過程

#### Gemini API 錯誤

**常見錯誤**：

| 錯誤代碼 | 原因 | 解決方案 |
|---------|------|---------|
| 401 | 無效的 API 密鑰 | 驗證 GEMINI_API_KEY |
| 403 | 權限不足 | 檢查 API 配額和權限 |
| 429 | 請求過於頻繁 | 實現速率限制和重試 |
| 500 | 伺服器內部錯誤 | 重試或聯繫 Google 支持 |

**實現重試機制**：
```python
def translate(self, text: str, ...) -> Dict[str, any]:
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = model.generate_content(prompt)
            return {"success": True, ...}
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                return {"success": False, "error": str(e)}
            # 等待後重試
            time.sleep(2 ** retry_count)
```

### 4. 數據驗證錯誤

#### 無效的輸入

```python
# 驗證輸入文本
if not text or not isinstance(text, str):
    return {
        "success": False,
        "error": "輸入文本無效"
    }

# 清淨文本
text = sanitize_text(text)
```

**驗證規則**：
- 文本不能為空
- 文本必須是字符串類型
- 移除或拒絕控制字符

## 日誌記錄

### 日誌級別

```python
logger.debug()    # 詳細的診斷信息
logger.info()     # 正常操作信息
logger.warning()  # 警告信息
logger.error()    # 錯誤信息
logger.critical() # 嚴重錯誤
```

### 日誌示例

```python
# 檢測到語言
logger.debug(f"檢測到語言: {lang_code}")

# 成功翻譯
logger.info(f"翻譯成功 ({source_lang} → {target_lang})")

# 語言檢測失敗但使用預設值
logger.warning(f"語言檢測失敗: {str(e)}，使用預設值")

# 翻譯服務異常
logger.error(f"翻譯過程出錯: {str(e)}", exc_info=True)
```

### 敏感信息保護

**永遠不要記錄**：
- API 密鑰或令牌
- 用戶個人信息
- 密碼或認證信息

### 日誌文件位置

```
logs/
└── app.log  # 應用程式日誌
```

## 用戶友好的錯誤消息

### 設計原則

1. **不暴露技術細節**
   ```python
   # ❌ 不好
   "KeyError: 'translation_result'"
   
   # ✅ 好
   "抱歉，系統發生錯誤，請稍後重試。"
   ```

2. **提供可操作的建議**
   ```python
   # ❌ 不好
   "超過最大長度"
   
   # ✅ 好
   "消息過長，最多支持 1000 個字符。"
   ```

3. **保持溫暖和專業的語氣**
   ```python
   error_messages = {
       "length_exceeded": f"消息過長，最多支持 {Config.MAX_MESSAGE_LENGTH} 個字符。",
       "api_error": "抱歉，翻譯服務目前不可用。請稍後重試。",
       "system_error": "抱歉，系統發生錯誤。我們的團隊已收到通知。"
   }
   ```

## 全局異常處理

### Flask 錯誤處理器

```python
@app.errorhandler(400)
def bad_request(error):
    return {"error": "請求無效"}, 400

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"內部服務器錯誤: {str(error)}", exc_info=True)
    return {"error": "服務器內部錯誤"}, 500
```

## 測試錯誤情況

### 單元測試示例

```python
def test_translate_empty_text():
    """測試空文本翻譯"""
    translator = GeminiTranslator(api_key="test-key")
    result = translator.translate("")
    assert result["success"] is False
    assert "error" in result

def test_language_detection_failure():
    """測試語言檢測失敗的恢復"""
    detector = LanguageDetector()
    result = detector.detect_language("\x00\x01\x02")  # 控制字符
    assert result["language"] == "en"  # 應該使用預設值
```

## 一般最佳實踐

1. **快速失敗，優雅地恢復**
   - 及早檢測錯誤
   - 提供有意義的恢復選項

2. **記錄足夠的上下文**
   - 包含時間戳、用戶 ID、相關參數
   - 使用結構化日誌

3. **監控和警報**
   - 跟踪錯誤率
   - 設置重要錯誤的警報

4. **定期審查**
   - 分析錯誤日誌
   - 改進錯誤處理邏輯

## 生產環境注意事項

1. **配置適當的日誌級別**
   ```env
   LOG_LEVEL=WARNING  # 生產環境推薦
   ```

2. **設置外部日誌聚合**
   - 使用 ELK Stack、Splunk 等
   - 便於中央管理和分析

3. **實施錯誤追踪**
   - 使用 Sentry、Rollbar 等
   - 自動捕獲和報告異常

4. **定期演習故障恢復**
   - 測試 API 密鑰過期的情況
   - 測試 LINE API 不可用的情況
