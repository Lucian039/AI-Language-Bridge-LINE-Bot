# 使用說明

本文件提供 AI Language Bridge LINE Bot 的實際操作流程，從啟動到 LINE Webhook 串接一次完成。

## 1. 使用前確認

- 已完成安裝與環境設定（可先參考 setup.md）
- 已建立 LINE Messaging API Channel
- 已取得 Gemini API Key

## 2. 填寫環境變數

請編輯專案根目錄的 .env：

```env
LINE_CHANNEL_ACCESS_TOKEN=你的_LINE_Channel_Access_Token
LINE_CHANNEL_SECRET=你的_LINE_Channel_Secret
GEMINI_API_KEY=你的_Gemini_API_Key

FLASK_ENV=development
FLASK_DEBUG=False
PORT=5000
LOG_LEVEL=INFO

GEMINI_MODEL=gemini-1.5-flash
DEFAULT_TARGET_LANGUAGE=zh-TW
MAX_MESSAGE_LENGTH=1000
```

## 3. 啟動機器人

在專案根目錄執行：

```powershell
python main.py
```

看到類似訊息代表啟動成功：

```text
AI Language Bridge 翻譯機器人已啟動 (Port: 5000)
```

## 4. 設定 LINE Webhook

在 LINE Developers Console 設定：

- Webhook URL: https://你的公開網址/line/webhook
- 啟用 Use webhook

### 本機開發建議（使用 ngrok）

```powershell
ngrok http 5000
```

把 ngrok 產生的 HTTPS 網址填入 Webhook URL，例如：

```text
https://xxxx-xx-xx-xx-xx.ngrok-free.app/line/webhook
```

## 5. 實際使用方式

1. 用戶在 LINE 對機器人輸入任意文字。
2. 系統會自動檢測語言並翻譯為預設目標語言（zh-TW）。
3. 機器人回傳格式如下：

```text
《 English → Traditional Chinese 》
Original: Hello, how are you?
Translation: 你好，你好嗎？
```

## 6. 常見操作

### 6.1 修改預設翻譯目標語言

修改 .env：

```env
DEFAULT_TARGET_LANGUAGE=en
```

可用例子：

- zh-TW（繁體中文）
- zh-CN（簡體中文）
- en（英文）
- ja（日文）
- ko（韓文）

### 6.2 調整訊息長度上限

修改 .env：

```env
MAX_MESSAGE_LENGTH=1500
```

### 6.3 開啟除錯模式

修改 .env：

```env
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
```

## 7. 驗證功能是否正常

啟動後可先執行測試：

```powershell
pytest
```

你也可以只跑翻譯模組測試：

```powershell
pytest tests/test_translator.py -v
```

## 8. 常見問題

### 問題：啟動時顯示缺少必要環境變數

處理方式：

- 確認 .env 已存在於專案根目錄
- 確認三個必要欄位都有填值：
  - LINE_CHANNEL_ACCESS_TOKEN
  - LINE_CHANNEL_SECRET
  - GEMINI_API_KEY

### 問題：LINE 無法收到回覆

處理方式：

- 檢查 Webhook URL 是否可被外網連線
- 確認 URL 是 HTTPS
- 確認路徑為 /line/webhook
- 檢查 LINE Developers Console 的 Webhook 測試結果

### 問題：翻譯失敗或回應慢

處理方式：

- 檢查 Gemini API Key 是否有效
- 檢查 Google API 配額是否已用盡
- 查看 logs 內的錯誤日誌

## 9. 推薦日常流程

1. 啟動本機服務：python main.py
2. 啟動 ngrok：ngrok http 5000
3. 更新 LINE Webhook URL
4. 用 LINE 實際發送訊息測試
5. 根據結果調整 .env 與翻譯設定
