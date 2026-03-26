# AI-Language-Bridge-LINE-Bot
A context-aware, multi-language translation LINE Bot powered by Gemini AI. Optimized for natural conversations and nuanced linguistics beyond literal translation.

## 📚 文檔

### 快速開始
- [設置指南](docs/setup.md) - 安裝和配置方式
- [使用指南](docs/usage.md) - 基本用法和功能

### 技術文檔
- [項目結構](docs/PROJECT_STRUCTURE.md) - 工程化項目組織 ⭐ **新增**
- [系統架構](docs/ARCHITECTURE.md) - 系統設計和數據流 ⭐ **新增**
- [遷移指南](docs/MIGRATION_GUIDE.md) - 從舊結構遷移的步驟 ⭐ **新增**
- [API 結構](docs/api_structure.md) - API 端點說明
- [錯誤處理](docs/error_handling.md) - 錯誤管理和恢復

### 部署
- [部署指南](docs/guides/DEPLOYMENT_GUIDE.md) - 生產環境部署
- [快速回復指南](docs/guides/QUICK_REPLY_GUIDE.md) - 快速選單菜單配置

## 🏗️ 項目結構改進 (2026-03-26)

專案已整理成工程化結構：
- ✅ 更清晰的模塊組織
- ✅ 導入路徑統一化
- ✅ 常數和數據模型集中管理
- ✅ 工具函數模塊化
- ✅ 測試文件集中在 `tests/`
- ✅ 環境配置統一在 `configs/`

詳見 [項目結構](docs/PROJECT_STRUCTURE.md)

## 🚀 快速開始

```bash
# 1. 克隆專案
git clone <repository-url>
cd AI-Language-Bridge-LINE-Bot

# 2. 安裝依賴
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 開發環境

# 3. 配置環境變數
cp configs/.env.example .env
# 編輯 .env，填入 LINE 和 Gemini API 密鑰

# 4. 運行應用
python main.py

# 5. 運行測試
pytest tests/ -v
```
