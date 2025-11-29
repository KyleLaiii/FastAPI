# Emogo Backend 快速開始指南

## 📋 專案概況

這是一個完整的 FastAPI 後端服務，用於 Emogo 情緒追蹤應用程式，具備以下功能：

- 🎬 接收 React Native 前端的情緒紀錄 JSON
- 💾 將資料儲存至 MongoDB Atlas
- 📊 提供 HTML 表格查看界面
- 📥 提供 CSV 下載功能
- ☁️ 可部署至 Render 平台

## 🚀 快速開始 (5分鐘)

### 第1步：建立虛擬環境

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 第2步：安裝依賴

```bash
pip install -r requirements.txt
```

### 第3步：設定環境變數

複製 `.env.example` 為 `.env`，並填入你的 MongoDB Atlas 連線字串：

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=emogo
MONGODB_COLLECTION_NAME=records
```

**如何取得 MONGODB_URI:**
1. 登入 [MongoDB Atlas](https://cloud.mongodb.com)
2. 選擇你的 Cluster
3. 點擊 "Connect"
4. 選擇 "Connect your application"
5. 複製連線字串，把 `<password>` 替換為你的密碼

### 第4步：啟動應用程式

```bash
uvicorn main:app --reload
```

應用程式將在 `http://localhost:8000` 運行

### 第5步：測試功能

**查看 API 文件:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**查看記錄表格:**
- HTML 表格: http://localhost:8000/export

**測試 POST 端點 (使用 PowerShell):**
```powershell
$body = @{
    exportDate = "2025-11-27T13:48:05.599Z"
    recordCount = 1
    records = @(
        @{
            id = 1
            sentiment = "較好"
            sentimentValue = 4
            latitude = 25.015
            longitude = 121.529
            timestamp = "2025-11-27T13:44:39.231Z"
            videoPath = "file:///path/to/video.mp4"
        }
    )
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/records" `
    -Method Post `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body
```

**測試 POST 端點 (使用 curl):**
```bash
curl -X POST "http://localhost:8000/records" \
  -H "Content-Type: application/json" \
  -d '{
    "exportDate": "2025-11-27T13:48:05.599Z",
    "recordCount": 1,
    "records": [{
      "id": 1,
      "sentiment": "較好",
      "sentimentValue": 4,
      "latitude": 25.015,
      "longitude": 121.529,
      "timestamp": "2025-11-27T13:44:39.231Z",
      "videoPath": "file:///path/to/video.mp4"
    }]
  }'
```

## 📁 專案結構

```
emogo-backend/
├── main.py                    # FastAPI 主應用（270行）
│   ├── Pydantic Models (Record, ExportPayload)
│   ├── MongoDB 連線管理
│   ├── 4個 API 端點 (GET /, POST /records, GET /export, GET /export/csv)
│   └── 完整的 async/await 實現
│
├── templates/
│   └── export.html           # Jinja2 HTML 模板（313行）
│       ├── 響應式設計
│       ├── 美觀的表格展示
│       ├── 彩色情緒標籤
│       └── CSV 下載連結
│
├── requirements.txt          # 依賴套件
│   ├── fastapi[all]
│   ├── uvicorn[standard]
│   ├── motor (MongoDB async driver)
│   ├── python-dotenv
│   └── jinja2
│
├── .env.example             # 環境變數範本
├── .env                     # 實際環境變數 (需要建立)
├── render.yaml              # Render 部署配置
├── README.md                # 完整開發文件
└── test_models.py          # 模型驗證測試檔案
```

## 🔌 API 端點詳細說明

### 1. GET `/` - 健康檢查

```
回應範例:
{
  "message": "Emogo backend is running",
  "endpoints": {
    "POST /records": "Submit emotion records from the app",
    "GET /export": "View all records as HTML table",
    "GET /export/csv": "Download all records as CSV file"
  }
}
```

### 2. POST `/records` - 提交情緒紀錄

**輸入 (JSON):**
```json
{
  "exportDate": "2025-11-27T13:48:05.599Z",
  "recordCount": 2,
  "records": [
    {
      "id": 7,
      "sentiment": "較好",
      "sentimentValue": 4,
      "latitude": 25.01550096033449,
      "longitude": 121.52929587923619,
      "timestamp": "2025-11-27T13:44:39.231Z",
      "videoPath": "file:///var/mobile/Containers/Data/Application/.../video_1764251069203.mp4"
    },
    {
      "id": 6,
      "sentiment": "較差",
      "sentimentValue": 2,
      "latitude": 25.018990501537225,
      "longitude": 121.53636330146826,
      "timestamp": "2025-11-27T09:48:46.699Z",
      "videoPath": "file:///var/mobile/Containers/Data/Application/.../video_1764236916672.mp4"
    }
  ]
}
```

**輸出 (JSON):**
```json
{
  "inserted": 2,
  "message": "Successfully inserted 2 record(s)"
}
```

**工作流程:**
1. 接收 ExportPayload
2. 驗證資料格式（FastAPI 自動處理）
3. 為每筆 record 添加 exportDate 欄位
4. 使用 `insert_many` 批量寫入 MongoDB
5. 返回插入筆數

### 3. GET `/export` - HTML 表格展示

**返回:** HTML 頁面，包含：
- 標題：「🎬 Emogo 使用紀錄」
- 紀錄統計：共計 X 筆紀錄
- CSV 下載連結
- 完整的表格，欄位包括：
  - ID, 心情 (彩色標籤), 心情值, 緯度, 經度, 記錄時間, 上傳時間, 影片路徑
- 響應式設計，支援行動裝置檢視

### 4. GET `/export/csv` - CSV 下載

**返回:** CSV 檔案 (emogo_records.csv)

**格式:**
```
id,sentiment,sentimentValue,latitude,longitude,timestamp,exportDate,videoPath
7,較好,4,25.01550096033449,121.52929587923619,2025-11-27T13:44:39.231000,...
6,較差,2,25.018990501537225,121.53636330146826,2025-11-27T09:48:46.699000,...
```

**特性:**
- 自動下載檔案名: emogo_records.csv
- 含有完整的欄位標題
- 按 timestamp 排序 (舊到新)
- 支援 Excel 開啟

## 🌐 部署到 Render

### 準備步驟

1. **GitHub 倉庫**
   - 將專案 push 到 GitHub
   - 確保 requirements.txt 已更新

2. **MongoDB Atlas**
   - 建立 MongoDB 帳戶和 Cluster
   - 建立應用程式使用者帳號
   - 取得連線字串

3. **Render 帳戶**
   - 在 render.com 建立帳號
   - 連接 GitHub 帳戶

### 部署步驟

1. **在 Render 建立 Web Service**
   - 選擇你的 GitHub repository
   - Runtime: Python
   - Build Command: 自動檢測 (使用 pip install -r requirements.txt)
   - Start Command: 已在 render.yaml 中配置

2. **設定環境變數**
   在 Render 後台的 Environment 部分添加：
   ```
   MONGODB_URI = mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   MONGODB_DB_NAME = emogo
   MONGODB_COLLECTION_NAME = records
   ```

3. **設定 MongoDB Network Access**
   - 登入 MongoDB Atlas
   - 進入 Security > Network Access
   - 新增 IP Address: `0.0.0.0/0` (允許所有 IP)
   - 或只允許 Render 特定 IP

4. **Deploy**
   - 點擊 "Create Web Service"
   - Render 自動部署
   - 日誌會顯示部署進度

### 部署後驗證

部署完成後，訪問：
- `https://<render-app-name>.onrender.com/` - 健康檢查
- `https://<render-app-name>.onrender.com/export` - 查看表格
- `https://<render-app-name>.onrender.com/export/csv` - 下載 CSV

## 🔍 故障排查

### 問題: "ModuleNotFoundError: No module named 'motor'"

**解決:**
```bash
pip install -r requirements.txt
```

### 問題: MongoDB 連線失敗

**檢查清單:**
- ✓ MONGODB_URI 是否正確 (包含密碼)
- ✓ MongoDB Atlas Network Access 是否允許你的 IP
- ✓ 使用者帳號密碼是否正確
- ✓ Cluster 是否啟動

**本機測試:**
```python
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def test():
    client = AsyncIOMotorClient("你的MONGODB_URI")
    await client.admin.command('ping')
    print("✓ MongoDB 連線成功")

asyncio.run(test())
```

### 問題: .env 檔案未被讀取

**檢查:**
- ✓ .env 檔案是否在專案根目錄
- ✓ .env 檔案是否被 .gitignore 忽略
- ✓ 是否已安裝 python-dotenv: `pip install python-dotenv`

### 問題: Render 部署失敗

**檢查 Render Logs:**
- 查看 Render 後台的 Logs 部分
- 確認 Start Command 是否正確
- 確認所有環境變數已設定

**常見錯誤:**
- `Port must be specified` → Start Command 應包含 `$PORT`
- `Module not found` → requirements.txt 未更新
- `Authentication failed` → MONGODB_URI 或密碼錯誤

## 📝 開發筆記

### 非同步編程 (Async/Await)

所有 API 端點都使用 `async def`，提供更好的效能：

```python
@app.post("/records")
async def submit_records(payload: ExportPayload):
    # 非同步 MongoDB 操作
    result = await mongodb_collection.insert_many(documents)
    return {"inserted": len(result.inserted_ids)}
```

### MongoDB 連線管理

應用程式會自動管理連線生命週期：

```python
@app.on_event("startup")
async def startup_event():
    await connect_to_mongodb()  # 啟動時連接

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongodb()  # 關閉時斷開
```

### Jinja2 模板

HTML 模板支援動態資料渲染：

```html
{% for record in records %}
    <tr>
        <td>{{ record.id }}</td>
        <td>{{ record.sentiment }}</td>
        <td>{{ record.sentimentValue }}/5</td>
    </tr>
{% endfor %}
```

## 💡 使用建議

1. **本機開發**
   - 使用 `--reload` flag 自動重新載入
   - 使用 Swagger UI (`/docs`) 測試 API
   - 查看終端日誌除錯

2. **資料備份**
   - 定期備份 MongoDB 資料
   - 使用 MongoDB Atlas 的備份功能

3. **效能優化**
   - 為 MongoDB collection 建立索引
   - 使用 motor 的非同步特性
   - 考慮使用資料庫連線池

4. **安全性**
   - 不要在版本控制中提交 .env 檔案
   - 使用強密碼和環境變數
   - 定期更新依賴套件

## 📞 需要幫助？

- 查看 FastAPI 文件: https://fastapi.tiangolo.com/
- 查看 MongoDB Motor 文件: https://motor.readthedocs.io/
- 查看 Render 部署指南: https://render.com/docs/

---

**祝部署順利！🚀**
