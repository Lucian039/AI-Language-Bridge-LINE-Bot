# API 結構和架構說明

## 項目架構概述

```
AI Language Bridge LINE Bot
│
├── 線上層 (Web Interface)
│   └── Flask Web Server
│
├── LINE Bot 層
│   ├── Webhook 端點 (/line/webhook)
│   ├── 事件驗證 (簽名檢查)
│   └── 消息路由
│
├── 翻譯服務層
│   ├── 語言檢測 (langdetect)
│   ├── Gemini 翻譯 (Google API)
│   └── 結果驗證
│
└── 數據層
    ├── 環境配置
    ├── 日誌系統
    └── 錯誤處理
```

## 模組結構

### 1. 主應用模組 (`main.py`)

**職責**：應用程式的入口和初始化

```python
create_app()  # 創建 Flask 應用實例
```

**關鍵步驟**：
1. 加載環境變數
2. 驗證必要的配置
3. 創建 Flask 應用
4. 註冊 LINE Bot Blueprint
5. 啟動 Web 服務器

### 2. 配置模組 (`src/config.py`)

**職責**：集中管理應用配置

**類**：
- `Config`：基礎配置
- `DevelopmentConfig`：開發環境配置
- `TestingConfig`：測試環境配置
- `ProductionConfig`：生產環境配置

**使用方式**：
```python
from src.config import Config
access_token = Config.LINE_CHANNEL_ACCESS_TOKEN
```

### 3. LINE Bot 模組 (`src/line_bot/`)

#### `handler.py`

**職責**：處理 LINE Webhook 事件

**功能**：
- `create_line_bot_handler()`：創建 LINE Bot Blueprint
- 簽名驗證
- 文本消息事件處理
- 錯誤恢復和日誌記錄

**事件流程**：
```
LINE 用戶消息
    ↓
Webhook 接收 (/line/webhook)
    ↓
簽名驗證 (X-Line-Signature)
    ↓
MessageEvent 解析
    ↓
validate_message_length()
    ↓
translator.translate()
    ↓
format_translation_message()
    ↓
line_bot_api.reply_message()
    ↓
回覆用戶
```

#### `utils.py`

**職責**：LINE Bot 相關的工具函數

**主要函數**：
- `validate_message_length()`：驗證消息長度
- `format_translation_message()`：格式化翻譯結果
- `extract_language_code()`：語言代碼提取
- `sanitize_text()`：文本清淨
- `split_long_message()`：消息分割

### 4. 翻譯模組 (`src/translator/`)

#### `gemini_translator.py`

**職責**：Gemini AI 翻譯引擎

**類**：`GeminiTranslator`

**主要方法**：
```python
def translate(
    text: str,
    target_language: Optional[str] = None,
    source_language: Optional[str] = None
) -> Dict[str, any]:
    """翻譯文本"""
    
def _build_translation_prompt(
    text: str,
    source_language: str,
    target_language: str
) -> str:
    """構建翻譯提示詞"""
```

**返回結構**：
```python
{
    "success": True/False,
    "translation": "翻譯結果",
    "source_language": "源語言名稱",
    "target_language": "目標語言名稱",
    "error": "錯誤信息 (如果失敗)"
}
```

#### `language_detector.py`

**職責**：自動語言檢測

**類**：`LanguageDetector`

**主要方法**：
```python
def detect_language(text: str) -> Dict[str, str]:
    """檢測文本語言"""
    
def is_language_supported(language_code: str) -> bool:
    """檢查語言是否支持"""
    
def get_supported_languages() -> Dict[str, str]:
    """取得支持的語言列表"""
```

## API 流程圖

### 消息處理流程

```
┌─────────────────────┐
│  LINE 用戶發送消息   │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────────────┐
│  POST /line/webhook         │
│  Headers: X-Line-Signature  │
│  Body: JSON Event           │
└──────────┬──────────────────┘
           │
           ↓
┌─────────────────────────────┐
│  簽名驗證                     │
│  (InvalidSignatureError)     │
└──────────┬──────────────────┘
           │
           ├─ 失敗 → 返回 400
           │
           ↓ 成功
┌─────────────────────────────┐
│  解析 TextMessageEvent      │
└──────────┬──────────────────┘
           │
           ↓
┌─────────────────────────────┐
│  validate_message_length()  │
└──────────┬──────────────────┘
           │
           ├─ 超長 → 返回錯誤消息
           │
           ↓ 合有效
┌─────────────────────────────┐
│  translator.translate()      │
│  ├─ detect_language()        │
│  ├─ 調用 Gemini API         │
│  └─ 返回結果                 │
└──────────┬──────────────────┘
           │
           ↓
┌─────────────────────────────┐
│  format_translation_message()│
└──────────┬──────────────────┘
           │
           ↓
┌─────────────────────────────┐
│ line_bot_api.reply_message()│
└──────────┬──────────────────┘
           │
           ↓
┌─────────────────────────────┐
│  回覆消息到 LINE 用戶         │
└─────────────────────────────┘
```

## 錯誤處理流程

```
┌────────────────────────┐
│  異常發生                │
└────────┬───────────────┘
         │
         ├─ InvalidSignatureError
         │  └─ 返回 400 Bad Request
         │
         ├─ ValueError
         │  └─ 返回 500 Internal Server Error
         │
         ├─ LangDetectException
         │  └─ 使用預設語言，繼續處理
         │
         └─ 其他異常
            ├─ 記錄詳細日誌
            ├─ 向用戶回覆友好錯誤消息
            └─ 返回 204 No Content
```

## 配置優先級

1. **運行時參數**（最高優先級）
   - 函數參數

2. **環境變數**（.env 文件）
   - LINE_CHANNEL_ACCESS_TOKEN
   - GEMINI_API_KEY
   - 等等

3. **默認配置**（最低優先級）
   - Config 類中的預設值

## 安全機制

### 1. Webhook 簽名驗證
```
X-Line-Signature: <HMAC-SHA256 signature>
```
使用 LINE_CHANNEL_SECRET 驗證請求真實性。

### 2. API 密鑰管理
- 使用 `.env` 文件管理敏感信息
- `.env` 被添加到 `.gitignore`
- 永遠不要在代碼中硬編碼密鑰

### 3. 消息驗證
- 消息長度限制（默認 1000 字符）
- 文本清淨（移除控制字符）

### 4. 日誌記錄
- 不記錄敏感信息（API 密鑰、令牌）
- 詳細的錯誤堆棧跟踪用於調試
