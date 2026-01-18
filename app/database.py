import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# Use in-memory database with persistent connection
_connection = None

def get_connection():
    """Get or create database connection"""
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(":memory:", check_same_thread=False)
        _connection.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_text TEXT NOT NULL,
                priority TEXT NOT NULL,
                tasks TEXT NOT NULL,
                summary TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        _connection.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                metadata TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        _connection.commit()
        print("✅ Database initialized with requests and knowledge_base tables")
    return _connection

def log_request(input_text: str, priority: str, tasks: List[str], summary: str) -> int:
    """Log workflow execution to database"""
    conn = get_connection()
    cursor = conn.execute("""
        INSERT INTO requests (input_text, priority, tasks, summary, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (input_text, priority, json.dumps(tasks), summary, datetime.utcnow().isoformat()))
    conn.commit()
    return cursor.lastrowid

def get_history(limit: int = 10, priority_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get recent workflow executions with optional filtering"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    
    query = "SELECT id, input_text as query, priority, tasks, summary, timestamp FROM requests"
    params = []
    
    if priority_filter:
        query += " WHERE priority = ?"
        params.append(priority_filter)
    
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    
    cursor = conn.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]

def get_count() -> int:
    """Get total number of requests"""
    conn = get_connection()
    cursor = conn.execute("SELECT COUNT(*) FROM requests")
    return cursor.fetchone()[0]

def add_knowledge(content: str, metadata: Dict[str, Any] = None) -> int:
    """Add content to knowledge base"""
    conn = get_connection()
    cursor = conn.execute("""
        INSERT INTO knowledge_base (content, metadata, timestamp)
        VALUES (?, ?, ?)
    """, (content, json.dumps(metadata or {}), datetime.utcnow().isoformat()))
    conn.commit()
    return cursor.lastrowid

def search_knowledge(query: str, limit: int = 3) -> List[str]:
    """Simple keyword search in knowledge base"""
    conn = get_connection()
    cursor = conn.execute("""
        SELECT content FROM knowledge_base 
        WHERE content LIKE ? 
        ORDER BY timestamp DESC LIMIT ?
    """, (f"%{query}%", limit))
    return [row[0] for row in cursor.fetchall()]