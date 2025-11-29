# Emogo Backend - 部署檢查清單

## ✅ 本機開發準備

### 環境設定
- [ ] 安裝 Python 3.8+ (`python --version`)
- [ ] 建立虛擬環境 (`.venv`)
- [ ] 啟動虛擬環境
- [ ] 安裝依賴 (`pip install -r requirements.txt`)

### 本機設定
- [ ] 建立 `.env` 檔案 (基於 `.env.example`)
- [ ] 設定 `MONGODB_URI` (MongoDB Atlas 連線字串)
- [ ] 設定 `MONGODB_DB_NAME` (預設: emogo)
- [ ] 設定 `MONGODB_COLLECTION_NAME` (預設: records)

### 本機測試
- [ ] 啟動應用: `uvicorn main:app --reload`
- [ ] 訪問 http://localhost:8000/ (健康檢查)
- [ ] 訪問 http://localhost:8000/docs (Swagger UI)
- [ ] 測試 POST /records (使用 curl 或 Postman)
- [ ] 測試 GET /export (查看 HTML 表格)
- [ ] 測試 GET /export/csv (下載 CSV 檔案)

## ☁️ Render 部署準備

### GitHub 倉庫
- [ ] 將專案推到 GitHub
- [ ] 確認 requirements.txt 已正確更新
- [ ] 確認 .gitignore 包含 `.env`
- [ ] 確認 render.yaml 存在且配置正確

### MongoDB Atlas 設定
- [ ] 建立 MongoDB Atlas 帳戶
- [ ] 建立 Cluster
- [ ] 建立應用程式使用者帳號 (記住用戶名和密碼)
- [ ] 複製連線字串 (格式: `mongodb+srv://username:password@...`)
- [ ] 設定 Network Access 為 `0.0.0.0/0`

### Render 帳戶
- [ ] 在 render.com 建立帳戶
- [ ] 連接 GitHub 帳戶
- [ ] 關聯 GitHub Repository

## 🚀 部署步驟

### 第1步：在 Render 建立 Web Service
- [ ] 點選 "New +"
- [ ] 選擇 "Web Service"
- [ ] 連接 GitHub Repository (emogo-backend-KyleLaiii)
- [ ] 設定服務名稱 (例: emogo-backend)

### 第2步：設定部署選項
- [ ] Runtime: Python (自動檢測)
- [ ] Build Command: 保持預設 (自動執行 pip install)
- [ ] Start Command: 應為 `uvicorn main:app --host 0.0.0.0 --port $PORT`
  (已在 render.yaml 中設定)

### 第3步：設定環境變數
在 Render 的 "Environment" 部分新增：

```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=emogo
MONGODB_COLLECTION_NAME=records
```

**重要:** 替換為你實際的 MongoDB Atlas 連線資訊

### 第4步：部署
- [ ] 點選 "Create Web Service"
- [ ] 等待部署完成 (通常 2-5 分鐘)
- [ ] 查看部署日誌確認沒有錯誤

## 🔍 部署後驗證

### 應用程式狀態
- [ ] 訪問 `https://<service-name>.onrender.com/`
- [ ] 應該看到 JSON 回應: `{"message": "Emogo backend is running", ...}`
- [ ] 查看 Render Logs 確認應用程式執行正常

### 功能測試
- [ ] 訪問 `https://<service-name>.onrender.com/export`
  (應顯示 HTML 表格，初始時為空)
- [ ] 訪問 `https://<service-name>.onrender.com/export/csv`
  (應自動下載 CSV 檔案)

### MongoDB 連線測試
- [ ] 使用 curl 或 Postman 測試 POST /records
- [ ] 提交一筆測試資料
- [ ] 查看 /export 是否顯示新資料

## 🐛 部署常見問題

### 問題: Build 失敗 (Module not found)
**解決:**
- [ ] 檢查 requirements.txt 是否包含所有依賴
- [ ] 確認 requirements.txt 格式正確 (每行一個套件)

### 問題: Start 失敗
**解決:**
- [ ] 檢查 render.yaml 中的 Start Command
- [ ] 確認包含 `$PORT` 變數
- [ ] 查看 Render Logs 取得詳細錯誤資訊

### 問題: MongoDB 連線超時
**解決:**
- [ ] 確認 MONGODB_URI 正確 (包含密碼)
- [ ] 檢查 MongoDB Atlas Network Access 是否開放 (0.0.0.0/0)
- [ ] 確認使用者帳號和密碼正確
- [ ] 檢查 MongoDB Cluster 是否正在運行

### 問題: POST /records 返回 500 錯誤
**解決:**
- [ ] 查看 Render Logs
- [ ] 確認傳送的 JSON 格式正確
- [ ] 驗證所有必需欄位都已包含

## 📊 部署後監控

### 定期檢查
- [ ] 查看 Render Logs (應無錯誤)
- [ ] 監控應用程式性能
- [ ] 檢查 MongoDB 儲存空間使用

### 維護任務
- [ ] 定期備份 MongoDB 資料
- [ ] 更新依賴套件版本 (monthly)
- [ ] 檢查應用程式更新

## 🔐 安全性檢查

### 代碼安全
- [ ] 確認 `.env` 已加入 .gitignore
- [ ] 確認沒有在代碼中硬編碼密碼
- [ ] 使用環境變數管理敏感資訊

### 應用程式安全
- [ ] 確認 CORS 設定適當 (如需要)
- [ ] 檢查輸入驗證 (Pydantic 自動處理)
- [ ] 考慮添加認證層 (如需要)

### 資料庫安全
- [ ] 確認 MongoDB Network Access 配置正確
- [ ] 使用強密碼
- [ ] 啟用 MongoDB 加密 (Atlas 預設啟用)

## 📞 聯絡方式

如部署過程中遇到問題：

1. **查看日誌**
   - Render: Logs 頁面
   - 本機: 終端輸出

2. **查閱文件**
   - README.md - 詳細開發指南
   - QUICK_START.md - 快速開始指南
   - FastAPI 文件: https://fastapi.tiangolo.com/
   - Render 文件: https://render.com/docs/

3. **測試環境變數**
   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('MONGODB_URI'))"
   ```

## ✨ 完成標記

- [ ] 本機開發測試完成
- [ ] 所有環境變數配置正確
- [ ] GitHub 倉庫已推送
- [ ] Render 部署完成
- [ ] 部署後功能驗證完成
- [ ] 應用程式正式上線

---

**祝部署成功！如有任何問題，請參考 README.md 和 QUICK_START.md。**
