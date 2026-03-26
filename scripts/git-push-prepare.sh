#!/bin/bash
# ============================================================================
# Git Push 準備指令清單
# AI Language Bridge LINE Bot - 工程化重構
# ============================================================================

echo "📋 ==== Git Push 準備步驟 ===="

# Step 1: 檢查當前分支
echo -e "\n1️⃣  當前分支："
git branch -v

# Step 2: 查看修改內容（簡要）
echo -e "\n2️⃣  修改內容摘要："
git status --short | head -20
echo "... (更多檔案)"

# Step 3: Stage 所有變更
echo -e "\n3️⃣  Stage 所有變更..."
git add -A
echo "✅ git add -A 完成"

# Step 4: 驗證 staged 文件
echo -e "\n4️⃣  Staged 檔案數量："
git diff --cached --name-only | wc -l
echo "檔案"

# Step 5: 創建 Commit
echo -e "\n5️⃣  建立 Commit..."
git commit -m "♻️ feat(refactor): 工程化專案結構重組

- ✨ 新增應用程式工廠 (app/factory.py)
- 📦 模組化核心代碼 (src/constants.py, models/, utils/)
- 🧪 集中測試框架 (tests/conftest.py, smoke/)
- 📚 分類文檔結構 (docs/guides, architecture, reports)
- ⚙️ 配置管理標準化 (configs/)
- 🔧 工具集中化 (scripts/)
- 📋 清理根目錄 (移除 13+ 散亂文件)
- 🔐 完善 .gitignore 與敏感信息屏蔽

改進：
- 根目錄文件 25+ → 13 (48% 減少)
- 文檔組織度從分散到完全分層
- 所有路徑引用已更新
- 完全保持向後相容性

詳見 docs/ROOT_DIRECTORY_CLEANUP.md"

# Step 6: 查看 Log
echo -e "\n6️⃣  最新 Commit："
git log -1 --oneline

# Step 7: Push 提示
echo -e "\n7️⃣  準備 Push..."
echo "執行以下命令推送到遠端："
echo -e "\n  \033[32mgit push origin main\033[0m"
echo -e "\n或指定分支："
echo -e "\n  \033[32mgit push origin $(git rev-parse --abbrev-ref HEAD)\033[0m"

# Step 8: 最終確認
read -p "按 Enter 開始推送... (Ctrl+C 中止)"

# Step 9: 執行 Push
echo -e "\n8️⃣  執行 Push..."
git push origin $(git rev-parse --abbrev-ref HEAD) -v

echo -e "\n✅ 推送完成！"
echo "🎉 項目工程化重組已成功提交到遠端"
