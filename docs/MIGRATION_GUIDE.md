# 📋 項目重構遷移指南

> 本指南說明如何從舊的專案結構遷移到新的工程化結構

## 🔄 遷移步驟

### 1. 備份原始代碼 ✅

```bash
# 建議在開始前建立備份分支
git checkout -b backup/old-structure
git commit -am "Backup: Old project structure"
git checkout main
```

### 2. 驗證新結構已建立 ✅

新的目錄已建立：
- ✅ `src/constants.py` - 常數定義
- ✅ `src/models/` - 數據模型
- ✅ `src/utils/` - 工具函數
- ✅ `app/factory.py` - 應用工廠
- ✅ `configs/` - 環境配置
- ✅ `tests/conftest.py` - Pytest 配置
- ✅ `requirements-dev.txt` - 開發依賴
- ✅ `pytest.ini` - Pytest 配置

### 3. 環境配置遷移 🔧

```bash
# 1. 複製舊的 .env 到 configs/
cp .env configs/.env.development

# 2. 或按 configs/.env.example 重新配置
cp configs/.env.example .env
# 編輯 .env，填入你的 API 密鑰
```

### 4. 清理舊的配置文件 🗑️

**舊結構中的廢棄文件**（可現在或之後刪除）：
- `app/config.py` - 已整合到 `src/config.py`
- `app/handler.py` - 相關代碼已轉移到 `src/line_bot/handler.py`

### 5. 測試文件遷移 🧪

根目錄的測試文件已集中到 `tests/smoke/` (快速測試層)：
- `test_gemini_quick.py` → `tests/smoke/test_gemini_quick.py`
- `test_quick_reply.py` → `tests/smoke/test_quick_reply.py`

其他測試組織方式：
- `tests/unit/` - 單元測試
- `tests/integration/` - 集成測試
- `tests/smoke/` - 快速功能測試
- `tests/fixtures/` - 測試夾具和模擬數據

### 6. 文檔結構遷移 📚

根目錄的文檔已按用途分類到 `docs/`：
- `DEPLOYMENT_GUIDE.md` → `docs/guides/DEPLOYMENT_GUIDE.md`
- `QUICK_REPLY_GUIDE.md` → `docs/guides/QUICK_REPLY_GUIDE.md`
- `IMPLEMENTATION_DETAILS.md` → `docs/architecture/IMPLEMENTATION_DETAILS.md`
- `CODE_SUMMARY.md` → `docs/reports/CODE_SUMMARY.md`
- `REFACTORING_SUMMARY.md` → `docs/reports/REFACTORING_SUMMARY.md`

### 7. 工具指令集中 🔧

根目錄的工具檔已移至 `scripts/`：
- `check_models.py` → `scripts/check_models.py`

### 8. 更新應用入口 📝

**舊版本** (`main.py` 原版本)：
```python
from app.config import Config
from app.handler import line_webhook_bp

def create_app():
    # 應用創建邏輯...
```

**新版本** (`main.py` 新)：
```python
from app.factory import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(...)
```

### 使用新的 main.py：

```bash
# main_new.py 已整併到 main.py，無需備份
mv main.py main_backup.py

# 使用新版本
mv main_new.py main.py

# 或直接編輯 main.py 按照新版本改寫
```

### 7. 依賴管理更新 📦

新增開發依賴支持：
```bash
# 安裝開發依賴
pip install -r requirements-dev.txt

# 檢查導入沒有問題
python -m pytest --collect-only
```

### 8. 驗證遷移成功 ✔️

```bash
# 1. 健康檢查
python main.py
# 應該看到: 🚀 AI Language Bridge 翻譯機器人已啟動 (Port: 5000)

# 2. 運行測試
pytest tests/ -v --tb=short

# 3. 代碼質量檢查
black src/ tests/ --check
flake8 src/ tests/

# 4. 導入檢查
python -c "from src.constants import TranslationMode; print('✅ 導入成功')"
python -c "from src.models import TranslationRequest; print('✅ 導入成功')"
```

## 📋 檢查清單

遷移完成後的驗證清單：

- [ ] 新的目錄結構已建立
- [ ] 環境變數已配置（`.env` 文件）
- [ ] `python main.py` 能正常啟動
- [ ] `pytest tests/ -v` 通過所有測試
- [ ] 舊的配置和處理器文件已備份或刪除
- [ ] 導入路徑已更新
- [ ] 代碼質量檢查通過（black, flake8）
- [ ] 項目可以成功部署

## 🔗 快速參考

### 導入路徑變更

| 舊導入 | 新導入 | 說明 |
|-------|-------|------|
| `from app.config import Config` | `from src.config import Config` | 配置管理 |
| `from app.handler import ...` | `from src.line_bot.handler import ...` | LINE 處理器 |
| `from app.factory import create_app` | `from app.factory import create_app` | 應用工廠（新增） |

### 新增模塊導入

```python
# 常數
from src.constants import TranslationMode, DEFAULT_TRANSLATION_MODE

# 數據模型
from src.models import TranslationRequest, TranslationResponse, UserPreference

# 工具函數
from src.utils import setup_logging, format_message, truncate_text
```

## 常見問題

### Q1: 如何回滾到舊結構？

```bash
# 使用之前建立的備份分支
git checkout backup/old-structure
```

### Q2: 舊的 `app/config.py` 還需要嗎？

不需要。所有配置管理已遷移到 `src/config.py`。

### Q3: 對現有功能有影響嗎？

無。遷移只是調整代碼組織，不改變業務邏輯。

### Q4: 如何在其他項目中使用新的模塊結構？

見 [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)

## 需要幫助？

- 查看 [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - 項目結構詳解
- 查看 [setup.md](./setup.md) - 安裝和環境設置
- 查看 [usage.md](./usage.md) - 使用指南

---

**遷移完成日期**：2026-03-26
