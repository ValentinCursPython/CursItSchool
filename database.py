import sqlite3

DB_NAME = "expenses.db"

def get_connection():
    """Creează și returnează conexiunea la baza de date SQLite."""
    return sqlite3.connect(DB_NAME)

def init_db():
    """Creează tabelele users și expenses dacă nu există."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabel utilizatori
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT
        )
    """)

    # Tabel cheltuieli
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Baza de date a fost inițializată cu succes!")
