---
layout: default
title: 項目結構文檔
description: AI Language Bridge 翻譯機器人的工程化項目結構說明
---

# 📂 AI Language Bridge 項目結構

## 整體架構

```
AI-Language-Bridge-LINE-Bot/
│
├── 🔧 配置與部署層
│   ├── configs/                    # 環境配置文件
│   │   ├── .env.example            # 配置模板
│   │   ├── .env.development        # 開發環境配置
│   │   └── .env.production         # 生產環境配置
│   │
│   ├── infra/                      # 基礎設施配置
│   │   └── (Docker, K8s 配置等)
│   │
│   ├── requirements.txt            # 生產依賴
│   └── requirements-dev.txt        # 開發依賴
│
├── 🎯 應用層 (app/)
│   ├── __init__.py                 # 導出 create_app
│   ├── factory.py                  # Flask 應用工廠
│   ├── config.py                   # (已廢棄，轉移到 src/)
│   └── handler.py                  # (已廢棄，轉移到 src/)
│
├── 💻 核心代碼層 (src/)
│   ├── __init__.py
│   ├── constants.py                # 常數定義
│   ├── config.py                   # 配置管理類
│   │
│   ├── models/                     # 數據模型
│   │   └── __init__.py             # TranslationRequest, Response 等
│   │
│   ├── utils/                      # 工具函數
│   │   └── __init__.py             # 日誌、格式化、解析等
│   │
│   ├── line_bot/                   # LINE Bot 模塊
│   │   ├── __init__.py
│   │   ├── handler.py              # Webhook 事件處理
│   │   └── utils.py                # LINE 相關工具函數
│   │
│   └── translator/                 # 翻譯模塊
│       ├── __init__.py
│       ├── gemini_translator.py    # Gemini API 實現
│       └── language_detector.py    # 語言檢測
│
├── 🧪 測試層 (tests/)
│   ├── conftest.py                 # pytest 配置和 fixtures
│   ├── __init__.py
│   │
│   ├── test_line_handler.py        # LINE 處理器測試
│   ├── test_translator.py          # 翻譯器測試
│   ├── test_gemini_quick.py        # 快速 Gemini 測試
│   ├── test_quick_reply.py         # 快速回復測試
│   │
│   └── fixtures/                   # 測試夾具
│       └── (模擬數據、示例等)
│
├── 📚 文檔層 (docs/)
│   ├── 基礎文檔
│   │   ├── api_structure.md        # API 結構文檔
│   │   ├── error_handling.md       # 錯誤處理文檔
│   │   ├── setup.md                # 安裝說明
│   │   └── usage.md                # 使用指南
│   │
│   ├── 架構文檔 (architecture/)
│   │   ├── PROJECT_STRUCTURE.md    # 項目結構說明
│   │   ├── ARCHITECTURE.md         # 系統架構設計
│   │   └── IMPLEMENTATION_DETAILS.md # 實現細節
│   │
│   ├── 指南 (guides/)
│   │   ├── DEPLOYMENT_GUIDE.md     # 生產環境部署
│   │   ├── QUICK_REPLY_GUIDE.md    # 快速回復配置
│   │   └── MIGRATION_GUIDE.md      # 項目遷移指南
│   │
│   └── 報告 (reports/)
│       ├── CODE_SUMMARY.md         # 代碼實現摘要
│       └── REFACTORING_SUMMARY.md  # 工程化改進報告
│
├── 📦 其他文件
│   ├── logs/                       # 日誌目錄
│   ├── scripts/                    # 工具指令
│   ├── main.py                     # 應用入口
│   ├── README.md                   # 項目說明
│   ├── pytest.ini                  # Pytest 配置
│   └── .env                        # 環境變數 (本地開發)
│
└── 📄 元數據
    ├── LICENSE                     # 授權證書
    └── .gitignore                  # Git 忽略規則
```

## 模塊說明

### 📦 src/ 核心模塊

| 模塊 | 職責 | 關鍵類/函數 |
|------|------|----------|
| `constants.py` | 應用常數、枚舉、配置值 | `TranslationMode`, `SUPPORTED_LANGUAGES` |
| `config.py` | 環境變數管理、配置驗證 | `Config` 類 |
| `models/` | 數據模型定義 | `TranslationRequest`, `TranslationResponse`, `UserPreference` |
| `utils/` | 通用工具函數 | `setup_logging()`, `format_message()`, `truncate_text()` |
| `line_bot/` | LINE Bot 集成 | `create_line_bot_handler()`, LINE Webhook 處理 |
| `translator/` | AI 翻譯引擎 | `GeminiTranslator`, `LanguageDetector` |

### 🎯 app/ 應用工廠層

| 文件 | 職責 |
|------|------|
| `factory.py` | 創建和配置 Flask 應用程序實例 |
| `__init__.py` | 導出 `create_app` 函數 |

### 🧪 tests/ 測試結構

- 使用 pytest 框架
- 所有測試文件統一在 `tests/` 目錄
- `conftest.py` 定義共享 fixtures
- 支持標記：`@pytest.mark.unit`, `@pytest.mark.integration` 等

## 配置管理

### 環境變數加載順序

```
1. .env.example       (默認模板)
2. .env.development   (開發環境)
3. .env.production    (生產環境)
4. 運行時傳入的密鑰   (最高優先級)
```

### 必需的環境變數

```env
# Flask 配置
FLASK_ENV=development|production
SECRET_KEY=your-secret-key

# LINE API
LINE_CHANNEL_SECRET=xxx
LINE_CHANNEL_ACCESS_TOKEN=xxx

# Gemini API
GEMINI_API_KEY=xxx
GEMINI_MODEL=gemini-1.5-flash
```

## 開發工作流

### 本地開發

```bash
# 1. 安裝依賴
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 2. 配置環境變數
cp configs/.env.example .env

# 3. 運行應用
python main.py

# 4. 運行測試
pytest tests/ -v
pytest tests/ --cov=src
```

### 代碼質量檢查

```bash
# 格式化代碼
black src/ tests/

# 檢查代碼風格
flake8 src/ tests/
pylint src/

# 排序導入
isort src/ tests/

# 類型檢查
mypy src/
```

## 數據流

```
LINE 用戶消息
    ↓
[app/factory.py] 創建 Flask 應用
    ↓
[src/line_bot/handler.py] 接收 Webhook
    ↓
驗證簽名 → 解析消息 → 構建 TranslationRequest (models/)
    ↓
[src/translator/gemini_translator.py] Gemini API 調用
    ↓
[src/line_bot/utils.py] 格式化 TranslationResponse
    ↓
LINE 回復消息
```

## 最佳實踐

### ✅ 應該做

- 所有配置通過 `src/config.py` 管理
- 常數定義在 `src/constants.py`
- 工具函數放在 `src/utils/`
- 數據模型放在 `src/models/`
- 每個功能模塊應有測試文件

### ❌ 不應該做

- 不要硬編碼 API 密鑰或敏感信息
- 不要在模塊間import時產生循環依賴
- 不要在 `src/` 中的文件直接操作 Flask app 對象
- 不要在根目錄散亂放置測試文件

## 下一步改進方向

1. **CI/CD 集成**：GitHub Actions/GitLab CI
2. **容器化**：Dockerfile, docker-compose
3. **日誌聚合**：ELK Stack 或 Datadog
4. **監控告警**：Prometheus + Grafana
5. **API 文檔**：Swagger/OpenAPI
6. **性能監控**：APM 工具集成

---

**最後更新**：2026-03-26
