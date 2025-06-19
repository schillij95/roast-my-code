import os
import sqlite3

# Determine database path; fallback to SQLite file if no DATABASE_URL provided
db_path = os.getenv("DATABASE_URL", "")
if db_path.startswith("sqlite:///"):
    db_path = db_path.split("sqlite:///")[1]
elif not db_path:
    db_path = os.path.join(os.path.dirname(__file__), os.pardir, "clapbacks.db")

conn = sqlite3.connect(db_path, check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
# Create table for storing shared clapbacks
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS clapbacks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        llm_response TEXT NOT NULL,
        audio_url TEXT,
        create_ts DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
)
conn.commit()

def insert_clapback(llm_response: str, audio_url: str = None) -> int:
    cursor.execute(
        "INSERT INTO clapbacks (llm_response, audio_url) VALUES (?, ?)",
        (llm_response, audio_url),
    )
    conn.commit()
    return cursor.lastrowid

def get_clapback(clapback_id: int):
    cursor.execute(
        "SELECT id, llm_response, audio_url, create_ts FROM clapbacks WHERE id = ?",
        (clapback_id,),
    )
    return cursor.fetchone()