"""
Database layer — SQLite for PoC.
Interface is intentionally thin so it can be swapped for asyncpg/PostgreSQL later.
"""
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.environ.get("DATABASE_PATH", str(Path(__file__).parent / "numbers.db")))


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS numbers (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                number_str TEXT UNIQUE NOT NULL,
                saved_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_number_str ON numbers(number_str)"
        )


def lookup_number(number_str: str) -> str | None:
    """Return saved_text for the given canonical number string, or None if not found."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT saved_text FROM numbers WHERE number_str = ?", (number_str,)
        ).fetchone()
    return row["saved_text"] if row else None


def save_number(number_str: str, saved_text: str) -> bool:
    """
    Insert a new number→text pair. Returns True on success, False if already exists.
    Pairs are immutable: a second insert for the same number is a no-op (returns False).
    """
    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO numbers (number_str, saved_text) VALUES (?, ?)",
                (number_str, saved_text),
            )
        return True
    except sqlite3.IntegrityError:
        return False
