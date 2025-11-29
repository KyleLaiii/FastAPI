"""
快速測試檔案 - 驗證 Pydantic 模型和 API 結構
使用方式: python test_models.py
"""

from datetime import datetime
import json

# 測試 Pydantic 模型（不需要 FastAPI 執行）
try:
    from pydantic import BaseModel
    from typing import List, Optional
    
    class Record(BaseModel):
        """Model for individual emotion record"""
        id: int
        sentiment: str
        sentimentValue: int
        latitude: Optional[float] = None
        longitude: Optional[float] = None
        timestamp: datetime
        videoPath: str

    class ExportPayload(BaseModel):
        """Model for the payload received from the React Native frontend"""
        exportDate: datetime
        recordCount: int
        records: List[Record]
    
    print("✓ Pydantic 模型導入成功")
    
    # 測試資料
    test_payload = {
        "exportDate": "2025-11-27T13:48:05.599Z",
        "recordCount": 1,
        "records": [
            {
                "id": 7,
                "sentiment": "較好",
                "sentimentValue": 4,
                "latitude": 25.01550096033449,
                "longitude": 121.52929587923619,
                "timestamp": "2025-11-27T13:44:39.231Z",
                "videoPath": "file:///var/mobile/Containers/Data/Application/video.mp4"
            }
        ]
    }
    
    # 驗證資料能否正確解析
    payload = ExportPayload(**test_payload)
    print("✓ ExportPayload 資料驗證成功")
    print(f"  - exportDate: {payload.exportDate}")
    print(f"  - recordCount: {payload.recordCount}")
    print(f"  - records 筆數: {len(payload.records)}")
    print(f"  - 第一筆記錄 ID: {payload.records[0].id}")
    print(f"  - 第一筆記錄情緒: {payload.records[0].sentiment}")
    
    print("\n✓ 所有模型驗證通過！")
    
except Exception as e:
    print(f"✗ 錯誤: {e}")
    import traceback
    traceback.print_exc()
