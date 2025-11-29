"""
Emogo Backend API Service

This FastAPI application handles data collection from the Emogo React Native frontend.
It provides endpoints for:
- Receiving emotion records with location and video data
- Exporting records as HTML table
- Exporting records as CSV file

Features:
- Async support using FastAPI and Motor (async MongoDB driver)
- MongoDB Atlas integration for data persistence
- HTML templating with Jinja2
- Environment variable configuration
"""

import os
import csv
import io
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

# Load environment variables from .env file in development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ============================================================================
# Configuration
# ============================================================================

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://Kyle:00000000@emogo.cyy5the.mongodb.net/emogo?retryWrites=true&w=majority")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "Emogo")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME", "records")

# ============================================================================
# Pydantic Models
# ============================================================================

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


# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title="Emogo Backend",
    description="API service for Emogo emotion tracking application",
    version="1.0.0"
)

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")
templates.env.globals["now"] = datetime.now  
# ============================================================================
# MongoDB Connection Management
# ============================================================================

# Global variables to hold MongoDB connection
mongodb_client: Optional[AsyncIOMotorClient] = None
mongodb_db: Optional[AsyncIOMotorDatabase] = None
mongodb_collection: Optional[AsyncIOMotorCollection] = None


async def connect_to_mongodb():
    """Establish connection to MongoDB Atlas on startup"""
    global mongodb_client, mongodb_db, mongodb_collection
    try:
        mongodb_client = AsyncIOMotorClient(MONGODB_URI)
        # Verify connection
        await mongodb_client.admin.command('ping')
        print("✓ Connected to MongoDB Atlas")
        
        mongodb_db = mongodb_client[MONGODB_DB_NAME]
        mongodb_collection = mongodb_db[MONGODB_COLLECTION_NAME]
        print(f"✓ Using database: {MONGODB_DB_NAME}, collection: {MONGODB_COLLECTION_NAME}")
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        raise


async def close_mongodb():
    """Close MongoDB connection on shutdown"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("✓ Closed MongoDB connection")


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    await connect_to_mongodb()


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    await close_mongodb()


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """
    Health check endpoint
    Returns basic information about available endpoints
    """
    return {
        "message": "Emogo backend is running",
        "endpoints": {
            "POST /records": "Submit emotion records from the app",
            "GET /export": "View all records as HTML table",
            "GET /export/csv": "Download all records as CSV file"
        }
    }


@app.post("/records")
async def submit_records(payload: ExportPayload):
    """
    POST endpoint to receive emotion records from the React Native frontend.
    
    Accepts a JSON payload containing:
    - exportDate: timestamp when the export was initiated
    - recordCount: number of records being exported
    - records: list of Record objects
    
    Each record is stored in MongoDB with the exportDate field added.
    
    Returns:
    - inserted: number of records successfully inserted
    """
    try:
        # Prepare documents for insertion
        documents = []
        for record in payload.records:
            doc = record.model_dump()
            doc["exportDate"] = payload.exportDate
            documents.append(doc)
        
        # Insert all records into MongoDB
        if documents:
            result = await mongodb_collection.insert_many(documents)
            inserted_count = len(result.inserted_ids)
            print(f"✓ Inserted {inserted_count} records into MongoDB")
            return {
                "inserted": inserted_count,
                "message": f"Successfully inserted {inserted_count} record(s)"
            }
        else:
            return {"inserted": 0, "message": "No records to insert"}
            
    except Exception as e:
        print(f"✗ Error inserting records: {e}")
        return {"error": str(e)}, 500


@app.get("/export", response_class=HTMLResponse)
async def export_html(request: Request):
    """
    GET endpoint to display all records as an HTML table.
    
    Retrieves all records from MongoDB, sorts them by timestamp (oldest first),
    and renders them using the Jinja2 template.
    
    Returns:
    - HTML page with a table of all records and a CSV download link
    """
    try:
        # Fetch all records from MongoDB, sorted by timestamp
        records = await mongodb_collection.find().sort("timestamp", 1).to_list(None)
        
        # Convert datetime objects to strings for template rendering
        for record in records:
            if isinstance(record.get("timestamp"), datetime):
                record["timestamp"] = record["timestamp"].isoformat()
            if isinstance(record.get("exportDate"), datetime):
                record["exportDate"] = record["exportDate"].isoformat()
            # Remove MongoDB ObjectId from display
            if "_id" in record:
                del record["_id"]
        
        # Render template with records
        return templates.TemplateResponse(
            "export.html",
            {"request": request, "records": records}
        )
        
    except Exception as e:
        print(f"✗ Error fetching records: {e}")
        return f"<h1>Error</h1><p>{str(e)}</p>"


@app.get("/export/csv")
async def export_csv():
    """
    GET endpoint to download all records as a CSV file.
    
    Retrieves all records from MongoDB, sorts them by timestamp,
    and streams them as a downloadable CSV file.
    
    Returns:
    - CSV file with all records (Content-Type: text/csv)
    """
    try:
        # Fetch all records from MongoDB, sorted by timestamp
        records = await mongodb_collection.find().sort("timestamp", 1).to_list(None)
        
        # Create CSV content in memory
        output = io.StringIO()
        fieldnames = [
            "id", "sentiment", "sentimentValue", "latitude", "longitude",
            "timestamp", "exportDate", "videoPath"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()
        
        # Write records
        for record in records:
            # Convert datetime objects to ISO format strings
            if isinstance(record.get("timestamp"), datetime):
                record["timestamp"] = record["timestamp"].isoformat()
            if isinstance(record.get("exportDate"), datetime):
                record["exportDate"] = record["exportDate"].isoformat()
            
            # Extract only the fields we need
            row = {field: record.get(field, "") for field in fieldnames}
            writer.writerow(row)
        
        # Return as streaming response with proper headers
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=emogo_records.csv"}
        )
        
    except Exception as e:
        print(f"✗ Error exporting CSV: {e}")
        return {"error": str(e)}, 500