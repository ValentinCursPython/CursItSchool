import hashlib
from datetime import datetime
from database import get_connection

# --- USER MANAGEMENT ---

def hash_password(password: str) -> str:
    """Returnează un hash SHA256 pentru parolă."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(email: str, password: str) -> int:
    """Creează un nou utilizator și returnează ID-ul lui."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (email, password, created_at) VALUES (?, ?, ?)",
        (email, hash_password(password), datetime.now().isoformat())
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def authenticate_user(email: str, password: str) -> int | None:
    """
    Verifică login-ul utilizatorului.
    Returnează user_id dacă autentificarea reușește, altfel None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE email=?", (email,))
    row = cursor.fetchone()
    conn.close()

    if row and row[1] == hash_password(password):
        return row[0]
    return None


# --- CRUD CHELTUIELI ---

def add_expense(user_id: int, amount: float, category: str, date: str, description: str = "") -> int:
    """
    Adaugă o cheltuială pentru un utilizator în baza de date.
    Returnează ID-ul cheltuielii inserate.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        (user_id, amount, category, date, description)
    )
    conn.commit()
    expense_id = cursor.lastrowid
    conn.close()
    return expense_id


def get_all_expenses(user_id: int) -> list[tuple]:
    """
    Returnează toate cheltuielile unui utilizator.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE user_id=? ORDER BY date DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_expense(expense_id: int, user_id: int, amount: float, category: str, date: str, description: str = "") -> None:
    """
    Actualizează o cheltuială existentă după ID (doar pentru utilizatorul respectiv).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE expenses SET amount=?, category=?, date=?, description=? WHERE id=? AND user_id=?",
        (amount, category, date, description, expense_id, user_id)
    )
    conn.commit()
    conn.close()


def delete_expense(expense_id: int, user_id: int) -> None:
    """
    Șterge o cheltuială după ID (doar pentru utilizatorul respectiv).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=? AND user_id=?", (expense_id, user_id))
    conn.commit()
    conn.close()


# --- FILTRARE & SORTARE CHELTUIELI ---

def get_expenses_by_category(user_id: int, category: str) -> list[tuple]:
    """
    Returnează cheltuielile filtrate după categorie pentru un utilizator.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE user_id=? AND category=? ORDER BY date DESC", (user_id, category))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_expenses_by_date_range(user_id: int, start_date: str, end_date: str) -> list[tuple]:
    """
    Returnează cheltuielile unui utilizator dintr-un interval de date.
    Datele trebuie să fie în format 'YYYY-MM-DD'.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM expenses WHERE user_id=? AND date BETWEEN ? AND ? ORDER BY date ASC",
        (user_id, start_date, end_date)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_expenses_sorted(user_id: int, by: str = "amount", order: str = "ASC") -> list[tuple]:
    """
    Returnează cheltuielile sortate după un câmp pentru un utilizator.
    by: 'amount', 'date', 'category'
    order: 'ASC' sau 'DESC'
    """
    valid_fields = ["amount", "date", "category"]
    if by not in valid_fields:
        raise ValueError(f"Câmp invalid pentru sortare: {by}")
    if order not in ["ASC", "DESC"]:
        raise ValueError(f"Ordine invalidă: {order}")

    conn = get_connection()
    cursor = conn.cursor()
    query = f"SELECT * FROM expenses WHERE user_id=? ORDER BY {by} {order}"
    cursor.execute(query, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows
