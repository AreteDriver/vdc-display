"""Read-only database connection for VDC-Display."""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DATABASE_PATH = os.environ.get("DATABASE_PATH", "data/logistics.db")


@contextmanager
def get_connection():
    """Get a read-only database connection."""
    db_path = Path(DATABASE_PATH)
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def query_df(sql: str, params: tuple = ()) -> list[dict]:
    """Execute a query and return results as list of dicts."""
    with get_connection() as conn:
        cursor = conn.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def query_one(sql: str, params: tuple = ()) -> dict | None:
    """Execute a query and return a single result."""
    results = query_df(sql, params)
    return results[0] if results else None
