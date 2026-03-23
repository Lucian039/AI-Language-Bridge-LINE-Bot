# 安裝和設置指南

## 前提條件

- Python 3.8 或更高版本
- pip 包管理器
- LINE Developer 賬户
- Google Cloud 賬户和 Gemini API 訪問權限

## 步驟 1: 克隆項目

```bash
git clone <repository-url>
cd AI-Language-Bridge-LINE-Bot
```

## 步驟 2: 創建虛擬環境

### 使用 venv（推薦）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 使用 conda

```bash
conda create -n line-bot python=3.11
conda activate line-bot
```

## 步驟 3: 安裝依賴

```bash
pip install -r requirements.txt
```

## 步驟 4: 配置環境變數

複製 `.env.example` 創建 `.env` 文件：

```bash
cp .env.example .env
```

編輯 `.env` 文件並填入你的 API 密鑰：

```env
# LINE Messaging API
LINE_CHANNEL_ACCESS_TOKEN=your_token_here
LINE_CHANNEL_SECRET=your_secret_here

# Google Gemini API
GEMINI_API_KEY=your_gemini_key_here

# 應用設置
FLASK_ENV=development
PORT=5000
```

### 取得 LINE Channel 配置

1. 訪問 [LINE Developers Console](https://developers.line.biz/en/)
2. 創建新的頻道（Channel）
3. 在 "Basic settings" 中找到 Channel Secret
4. 在 "Messaging API" 中找到 Channel Access Token

### 取得 Gemini API 密鑰

1. 訪問 [Google Cloud Console](https://console.cloud.google.com/)
2. 創建新項目或選擇現有項目
3. 啟用 Generative Language API
4. 創建 API 密鑰

## 步驟 5: 測試安裝

運行測試以確保一切正常工作：

```bash
# 運行所有測試
pytest

# 運行特定測試文件
pytest tests/test_translator.py -v

# 運行測試並生成覆蓋率報告
pytest --cov=src tests/
```

## 步驟 6: 運行應用

```bash
python main.py
```

應用將在 `http://localhost:5000` 上啟動。

## Webhook 配置

在 LINE Developers Console 中配置 Webhook URL：

```
https://your-domain.com/line/webhook
```

## 常見問題

### 問題：缺少環境變數
**解決方案**：確保 `.env` 文件已創建並填入所有必要的密鑰

### 問題：ImportError
**解決方案**：確保虛擬環境已激活，並運行 `pip install -r requirements.txt`

### 問題：Gemini API 認證失敗
**解決方案**：驗證 GEMINI_API_KEY 的有效性和配額限制

## 開發工具

### 代碼風格檢查

```bash
# 使用 flake8 檢查代碼風格
flake8 src/ tests/

# 使用 black 自動格式化代碼
black src/ tests/

# 使用 pylint 進行深度分析
pylint src/
```

### 調試

在開發環境中，設置 `FLASK_DEBUG=True` 以啟用調試模式：

```bash
export FLASK_DEBUG=True
python main.py
```

## 生產部署

### 使用 Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### 安全建議

1. **不要將 `.env` 提交到版本控制**
2. **定期檢查 API 用量和成本**
3. **使用環境特定的配置**
4. **啟用 HTTPS 用於生產環境**

## 監控和日誌

應用日誌存儲在 `logs/` 目錄中。配置日誌級別：

```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 更新依賴

定期運行以下命令以檢查和更新依賴：

```bash
pip list --outdated
pip install --upgrade -r requirements.txt
```
