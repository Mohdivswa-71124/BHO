"""
Resource Saver - FastAPI Backend
A simple API to receive and store saved resources from the browser extension.
"""

from datetime import datetime
from typing import Literal
import sqlite3
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

# Initialize FastAPI app
app = FastAPI(
    title="Resource Saver API",
    description="Backend API for the Resource Saver browser extension",
    version="1.0.0"
)

# Enable CORS for browser extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to extension origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
def get_db_path():
    db_url = os.getenv("DATABASE_URL", "sqlite:///resources.db")
    if db_url.startswith("sqlite:///"):
        return db_url.replace("sqlite:///", "")
    return "resources.db"

DATABASE_PATH = get_db_path()


def init_db():
    """Initialize SQLite database with resources table."""
    conn = sqlite3.connect(DATABASE_PATH, timeout=20)
    try:
        # Enable WAL mode for better concurrency (Write-Ahead Logging)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        cursor = conn.cursor()
        # Create new table without type constraint (allows custom types)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    finally:
        conn.close()


# Initialize database on startup
init_db()


# Pydantic models
class ResourceCreate(BaseModel):
    """Schema for creating a new resource."""
    title: str
    url: str
    type: str  # Allow any type string (not limited to predefined types)
    userEmail: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "How to Build a Browser Extension",
                "url": "https://example.com/article",
                "type": "article"
            }
        }
    }


class LDResourceCreate(BaseModel):
    """Schema for creating a new resource via LDAPI, allowing preserved IDs and timestamps."""
    id: int | None = None
    title: str
    url: str
    type: str
    created_at: str | None = None
    userEmail: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "title": "Preserved Resource",
                "url": "https://example.com/preserved",
                "type": "article",
                "created_at": "2023-01-01 12:00:00",
                "userEmail": "user@example.com"
            }
        }
    }


class ResourceResponse(BaseModel):
    """Schema for resource response."""
    id: int
    title: str
    url: str
    type: str
    created_at: str
    message: str


class ResourceList(BaseModel):
    """Schema for list of resources."""
    resources: list[dict]
    count: int


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Resource Saver API",
        "version": "1.0.0"
    }


@app.post("/save", response_model=ResourceResponse)
async def save_resource(resource: ResourceCreate):
    """
    Save a new resource to the database.
    
    - **title**: The title of the resource
    - **url**: The URL of the resource
    - **type**: Type of resource (article, youtube, or tool)
    """
    # Log the incoming request
    print("\n" + "="*50)
    print("📥 NEW RESOURCE RECEIVED")
    print("="*50)
    print(f"📌 Title: {resource.title}")
    print(f"🔗 URL: {resource.url}")
    print(f"📁 Type: {resource.type}")
    print(f"🕐 Time: {datetime.now().isoformat()}")
    print("="*50 + "\n")

    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=20)
        conn.execute("PRAGMA synchronous=NORMAL;")
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO resources (title, url, type) VALUES (?, ?, ?)",
            (resource.title, resource.url, resource.type)
        )
        
        resource_id = cursor.lastrowid
        conn.commit()
        
        # Fetch the created resource
        cursor.execute(
            "SELECT id, title, url, type, created_at FROM resources WHERE id = ?",
            (resource_id,)
        )
        row = cursor.fetchone()
    finally:
        if 'conn' in locals():
            conn.close()

        # Send to external webhook if configured
        webhook_url = os.getenv("EXTERNAL_WEBHOOK_URL")
        webhook_token = os.getenv("EXTERNAL_WEBHOOK_TOKEN")
        
        # Use email from request if provided, otherwise fallback to env for backward compatibility
        user_email = resource.userEmail or os.getenv("USER_EMAIL")

        if webhook_url:
            try:
                print(f"🚀 Sending to webhook: {webhook_url}")
                async with httpx.AsyncClient() as client:
                    headers = {}
                    if webhook_token:
                        headers["Authorization"] = f"Bearer {webhook_token}"
                    
                    payload = {
                        "id": row[0],
                        "title": row[1],
                        "url": row[2],
                        "type": row[3],
                        "created_at": row[4]
                    }
                    
                    if user_email:
                        payload["userEmail"] = user_email
                    
                    response = await client.post(webhook_url, json=payload, headers=headers)
                    if response.status_code >= 200 and response.status_code < 300:
                        print("✅ Webhook sent successfully")
                    else:
                        print(f"⚠️ Webhook failed with status: {response.status_code}")
                        try:
                            print(f"📄 Response body: {response.text}")
                        except:
                            pass
            except Exception as e:
                print(f"❌ Failed to send webhook: {e}")

        return ResourceResponse(
            id=row[0],
            title=row[1],
            url=row[2],
            type=row[3],
            created_at=row[4],
            message="Resource saved successfully!"
        )

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Resource with this URL already exists"
        )
    except Exception as e:
        print(f"❌ Error saving resource: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save resource: {str(e)}"
        )


@app.post("/ldapi/resources")
async def ldapi_save_resource(resource: LDResourceCreate):
    """
    LDAPI endpoint to save a resource.
    Supports preserving existing IDs and timestamps.
    Returns the raw resource data as stored in the database.
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=20)
        conn.execute("PRAGMA synchronous=NORMAL;")
        cursor = conn.cursor()
        
        # Determine which fields to insert based on what's provided
        fields = ["title", "url", "type"]
        values = [resource.title, resource.url, resource.type]
        
        if resource.id is not None:
            fields.append("id")
            values.append(resource.id)
            
        if resource.created_at is not None:
            fields.append("created_at")
            values.append(resource.created_at)
            
        placeholder = ", ".join(["?"] * len(fields))
        columns = ", ".join(fields)
        
        cursor.execute(
            f"INSERT OR REPLACE INTO resources ({columns}) VALUES ({placeholder})",
            tuple(values)
        )
        
        resource_id = resource.id if resource.id is not None else cursor.lastrowid
        conn.commit()
        
        # Fetch the created resource to verify
        cursor.execute(
            "SELECT id, title, url, type, created_at FROM resources WHERE url = ?",
            (resource.url,)
        )
        row = cursor.fetchone()
    finally:
        if 'conn' in locals():
            conn.close()

        if not row:
            raise Exception("Record inserted but could not be fetched immediately")

        # Return the raw record as a dict (matching DB storage)
        return {
            "id": row[0],
            "title": row[1],
            "url": row[2],
            "type": row[3],
            "created_at": row[4]
        }

    except Exception as e:
        print(f"❌ Error in LDAPI saving resource: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save resource via LDAPI: {str(e)}"
        )


@app.get("/resources", response_model=ResourceList)
async def get_resources():
    """Get all saved resources."""
    conn = sqlite3.connect(DATABASE_PATH, timeout=20)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, url, type, created_at FROM resources ORDER BY created_at DESC"
        )
        rows = cursor.fetchall()
    finally:
        conn.close()

    resources = [
        {
            "id": row[0],
            "title": row[1],
            "url": row[2],
            "type": row[3],
            "created_at": row[4]
        }
        for row in rows
    ]

    return ResourceList(resources=resources, count=len(resources))


@app.delete("/resources/{resource_id}")
async def delete_resource(resource_id: int):
    """Delete a resource by ID."""
    conn = sqlite3.connect(DATABASE_PATH, timeout=20)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM resources WHERE id = ?", (resource_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        conn.commit()
    finally:
        conn.close()
    
    return {"message": f"Resource {resource_id} deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print("\n🚀 Starting Resource Saver API...")
    print(f"📡 Server running at http://localhost:{port}")
    print(f"📚 API docs at http://localhost:{port}/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=port)
