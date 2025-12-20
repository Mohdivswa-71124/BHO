"""
Resource Saver - FastAPI Backend
A simple API to receive and store saved resources from the browser extension.
"""

from datetime import datetime
from typing import Literal
import sqlite3
import os

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
DATABASE_PATH = "resources.db"


def init_db():
    """Initialize SQLite database with resources table."""
    conn = sqlite3.connect(DATABASE_PATH)
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
    conn.close()


# Initialize database on startup
init_db()


# Pydantic models
class ResourceCreate(BaseModel):
    """Schema for creating a new resource."""
    title: str
    url: str
    type: str  # Allow any type string (not limited to predefined types)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "How to Build a Browser Extension",
                "url": "https://example.com/article",
                "type": "article"
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
        conn = sqlite3.connect(DATABASE_PATH)
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
        conn.close()

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


@app.get("/resources", response_model=ResourceList)
async def get_resources():
    """Get all saved resources."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, url, type, created_at FROM resources ORDER BY created_at DESC"
    )
    rows = cursor.fetchall()
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
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM resources WHERE id = ?", (resource_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Resource not found")
    
    conn.commit()
    conn.close()
    
    return {"message": f"Resource {resource_id} deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting Resource Saver API...")
    print("📡 Server running at http://localhost:8080")
    print("📚 API docs at http://localhost:8080/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=8080)
