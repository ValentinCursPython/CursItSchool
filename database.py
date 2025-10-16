import sqlite3
from typing import Optional

DB_NAME = "expenses.db"


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection to the project database."""
    return sqlite3.connect(DB_NAME)


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cur.fetchall()]
    return column in cols


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None


def init_db() -> None:
    """Create tables if not present and ensure required columns exist."""
    conn = get_connection()
    cur = conn.cursor()

    # users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT
        )
    """)

    # expenses
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # migrations: ensure is_admin on users
    if not _column_exists(conn, "users", "is_admin"):
        cur.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0")

    # user_settings (per-user payday + monthly budget)
    if not _table_exists(conn, "user_settings"):
        cur.execute("""
            CREATE TABLE user_settings (
                user_id INTEGER PRIMARY KEY,
                payday INTEGER NOT NULL DEFAULT 1,
                monthly_budget REAL NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("DB initialized ✅")
