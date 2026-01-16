"""Tests for database module."""

import pytest
import tempfile
import sqlite3
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDatabaseConnection:
    """Tests for database connection handling."""

    def test_missing_database_raises_error(self):
        """Should raise FileNotFoundError for missing database."""
        import os

        os.environ["DATABASE_PATH"] = "/nonexistent/path/db.sqlite"

        # Re-import to pick up new env var
        from modules import database
        import importlib

        importlib.reload(database)

        with pytest.raises(FileNotFoundError):
            with database.get_connection():
                pass

    def test_connection_is_readonly(self):
        """Connection should be read-only."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        # Create a test database
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.execute("INSERT INTO test VALUES (1)")
        conn.commit()
        conn.close()

        import os

        os.environ["DATABASE_PATH"] = db_path

        from modules import database
        import importlib

        importlib.reload(database)

        # Should be able to read
        with database.get_connection() as conn:
            result = conn.execute("SELECT * FROM test").fetchone()
            assert result[0] == 1

        # Should not be able to write
        with pytest.raises(sqlite3.OperationalError):
            with database.get_connection() as conn:
                conn.execute("INSERT INTO test VALUES (2)")

        # Cleanup
        Path(db_path).unlink()


class TestQueryHelpers:
    """Tests for query helper functions."""

    def test_query_df_returns_list(self):
        """query_df should return a list of dicts."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test (id INTEGER, name TEXT)")
        conn.execute("INSERT INTO test VALUES (1, 'Alice')")
        conn.execute("INSERT INTO test VALUES (2, 'Bob')")
        conn.commit()
        conn.close()

        import os

        os.environ["DATABASE_PATH"] = db_path

        from modules import database
        import importlib

        importlib.reload(database)

        results = database.query_df("SELECT * FROM test ORDER BY id")

        assert isinstance(results, list)
        assert len(results) == 2
        assert results[0] == {"id": 1, "name": "Alice"}
        assert results[1] == {"id": 2, "name": "Bob"}

        Path(db_path).unlink()

    def test_query_one_returns_single(self):
        """query_one should return a single dict or None."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test (id INTEGER, name TEXT)")
        conn.execute("INSERT INTO test VALUES (1, 'Alice')")
        conn.commit()
        conn.close()

        import os

        os.environ["DATABASE_PATH"] = db_path

        from modules import database
        import importlib

        importlib.reload(database)

        result = database.query_one("SELECT * FROM test WHERE id = 1")
        assert result == {"id": 1, "name": "Alice"}

        result = database.query_one("SELECT * FROM test WHERE id = 999")
        assert result is None

        Path(db_path).unlink()
