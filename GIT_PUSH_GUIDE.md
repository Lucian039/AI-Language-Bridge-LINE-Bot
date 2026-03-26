# 🚀 Git Push 完整指令清單

## 📋 執行步驟

在專案根目錄執行以下命令（按順序）：

### Step 1: 確認狀態
```bash
git status
```

### Step 2: Stage 所有變更
```bash
git add -A
```

### Step 3: 確認配置文件（樣本）被包含
```bash
git add -f configs/.env.example
git add -f configs/.env.development  
git add -f configs/.env.production
```

### Step 4: 建立 Commit
```bash
git commit -m "♻️ refactor: 工程化專案結構重組完成

- 新增應用工廠 (app/factory.py)
- 模組化代碼 (src/constants, models, utils)
- 集中測試 (tests/conftest, smoke/)
- 分類文檔 (docs/guides|architecture|reports)
- 配置標準化 (configs/)
- 工具集中化 (scripts/)
- 根目錄清理 (移除 13+ 散亂文件)
- 完善 .gitignore (敏感信息屏蔽)

改進：根目錄 25+ → 13 文件 (-48%)
詳見 docs/ROOT_DIRECTORY_CLEANUP.md"
```

### Step 5: 驗證 Commit
```bash
git log -1 --oneline
```

### Step 6: 推送到遠端
```bash
git push origin main -v
```

或者推送到你的分支：
```bash
git branch  # 查看當前分支
git push origin <branch-name> -v
```

---

## ✅ 推送前檢查清單

- [ ] `.gitignore` 已更新（屏蔽了 logs/, .env, infra/bin/ngrok.exe 等）
- [ ] 所有新文件已被 stage (`git add -A`)
- [ ] commit 訊息清晰明確
- [ ] 本地 git log 顯示新 commit
- [ ] 網絡連接正常
- [ ] 有遠端 repository 的 push 權限

---

## 🎯 屏蔽規則說明

`.gitignore` 已更新的關鍵屏蔽規則：

```
# 環境變數和敏感信息
.env                          # 本地環境（git ignore）
secrets/                      # 傭密文件夾
*.key, *.pem                  # SSL 密鑰

# 日誌檔案
logs/                         # 應用日誌
*.log                         # 所有日誌

# 本地工具
infra/bin/ngrok.exe          # ngrok 可執行文件

# IDE 配置
.vscode/
.idea/

# 依賴
venv/
__pycache__/
*.pyc

# 測試生成
.pytest_cache/
.coverage
htmlcov/

# 保持被追蹤（白名單）
!.env.example
!configs/.env.example
!configs/.env.development
!configs/.env.production
```

---

## 📊 推送統計

你即將推送：
- ✨ **新增**: app/factory.py, src/constants.py, src/models/, src/utils/, docs/*, pytest.ini, configs/, scripts/, tests/conftest.py, tests/smoke/, 等
- 🔄 **修改**: README.md, .gitignore, app/__init__.py, docs/PROJECT_STRUCTURE.md, 等
- 🗑️ **刪除**: DEPLOYMENT_GUIDE.md, QUICK_REPLY_GUIDE.md, test_*.py, check_models.py, main_new.py, 等（已移至子目錄）

---

## 🆘 常見問題

### Q1: 推送被拒絕？
```bash
# 若遠端有新更新，先pull
git pull origin main --rebase

# 或強制推送（謹慎使用）
git push origin main --force-with-lease
```

### Q2: Commit 訊息太長？
使用更簡短版本：
```bash
git commit -m "refactor: 工程化專案結構重組 - 根目錄整理、文檔分類、模塊化代碼、集中測試"
```

### Q3: 忘記 stage 某些文件？
```bash
git reset HEAD~1  # 撤銷最後的 commit
git add -A        # 重新 stage
git commit -m "..." # 重新 commit
```

---

## ✨ 推送後驗證

推送成功後：
1. 查看 GitHub/GitLab 網頁確認新 commit
2. 驗證 file tree 顯示新的目錄結構
3. 檢查 `.gitignore` 是否生效（logs/, .env 等不出現）

---

**推送日期**: 2026-03-26  
**專案版本**: 1.0 - 工程化完成版
