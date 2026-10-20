
import os
import sqlite3
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

# Load .env from the same folder as main.py
load_dotenv(BASE_DIR / ".env")

# SQLite database file
DB_PATH = BASE_DIR / "database.db"

app = FastAPI(title="Items API")

# API key must be sent in the "api-key" header
api_key_header = APIKeyHeader(
    name="api-key",
    auto_error=False
)


# --------------------------------------------------
# Database
# --------------------------------------------------

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        """)


@app.on_event("startup")
def startup():
    init_db()


# --------------------------------------------------
# API key authentication
# --------------------------------------------------

def check_key(key: Optional[str] = Depends(api_key_header)):
    allowed_keys = [
        value.strip()
        for value in os.getenv("API_KEYS", "").split(",")
        if value.strip()
    ]

    if not key or key not in allowed_keys:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )


# --------------------------------------------------
# Request model
# --------------------------------------------------

class Item(BaseModel):
    name: str
    description: Optional[str] = None


# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.get("/")
def home():
    return {"message": "Items API is running"}


@app.post("/items/", dependencies=[Depends(check_key)])
def create_item(item: Item):
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO items (name, description)
            VALUES (?, ?)
            """,
            (item.name, item.description)
        )

        return {
            "id": cursor.lastrowid,
            "name": item.name,
            "description": item.description
        }


@app.get("/items/", dependencies=[Depends(check_key)])
def get_items():
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT id, name, description
            FROM items
            ORDER BY id
            """
        ).fetchall()

        return [dict(row) for row in rows]


@app.get("/items/{item_id}", dependencies=[Depends(check_key)])
def get_item(item_id: int):
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT id, name, description
            FROM items
            WHERE id = ?
            """,
            (item_id,)
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Item not found"
            )

        return dict(row)


@app.delete("/items/{item_id}", dependencies=[Depends(check_key)])
def delete_item(item_id: int):
    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM items WHERE id = ?",
            (item_id,)
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Item not found"
            )

        return {"message": "Item deleted successfully"}
