from __future__ import annotations

from datetime import datetime, date
import calendar as _cal
import hashlib
import random
import string
from typing import Optional, List, Tuple
from database import get_connection, init_db

init_db()


# ---------- helpers ----------
def _hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def _normalize_email(email: str) -> str:
    return email.strip().lower()


# ---------- Users ----------
def create_user(email: str, password: str, is_admin: int = 0) -> int:
    email_n = _normalize_email(email)
    password = password.strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (email, password, created_at, is_admin) VALUES (?, ?, ?, ?)",
        (email_n, _hash_password(password), datetime.now().isoformat(), int(is_admin))
    )
    conn.commit()
    uid = cur.lastrowid
    # initialize default settings for this user
    cur.execute("INSERT OR IGNORE INTO user_settings (user_id, payday, monthly_budget) VALUES (?, 1, 0)", (uid,))
    conn.commit()
    conn.close()
    return uid


def authenticate_user(email: str, password: str) -> Optional[Tuple[int, int]]:
    email_n = _normalize_email(email)
    password = password.strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password, is_admin FROM users WHERE lower(email)=?", (email_n,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    uid, stored_hash, is_admin = row
    return (uid, is_admin) if stored_hash == _hash_password(password) else None


def list_users() -> List[Tuple[int, str, str, str, int]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, email, password, created_at, is_admin FROM users ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()
    return rows


def promote_user_to_admin(user_id: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_admin=1 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


def ensure_default_admin(email: str = "admin@local", password: str = "admin123") -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE is_admin=1 LIMIT 1")
    has_admin = cur.fetchone()
    if not has_admin:
        cur.execute(
            "INSERT INTO users (email, password, created_at, is_admin) VALUES (?, ?, ?, 1)",
            (_normalize_email(email), _hash_password(password.strip()), datetime.now().isoformat())
        )
        conn.commit()
        # default settings for admin if missing
        cur.execute("INSERT OR IGNORE INTO user_settings (user_id, payday, monthly_budget) VALUES ((SELECT id FROM users WHERE is_admin=1 LIMIT 1), 1, 0)")
        conn.commit()
    conn.close()


# ---------- Password reset (local/demo) ----------
def _gen_temp_password(length: int = 8) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def reset_password_local(email: str) -> Optional[str]:
    email_n = _normalize_email(email)
    tmp = _gen_temp_password(8)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE lower(email)=?", (email_n,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    cur.execute("UPDATE users SET password=? WHERE lower(email)=?", (_hash_password(tmp), email_n))
    conn.commit()
    conn.close()
    return tmp


# ---------- User settings (payday + monthly budget) ----------
def get_user_settings(user_id: int) -> Tuple[int, float]:
    """
    Returns (payday, monthly_budget). Ensures a row exists.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO user_settings (user_id, payday, monthly_budget) VALUES (?, 1, 0)", (user_id,))
    conn.commit()
    cur.execute("SELECT payday, monthly_budget FROM user_settings WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    payday, budget = row
    return int(payday), float(budget)


def update_user_settings(user_id: int, payday: int, monthly_budget: float) -> None:
    payday = max(1, min(31, int(payday)))
    monthly_budget = float(monthly_budget)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO user_settings (user_id, payday, monthly_budget) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET payday=excluded.payday, monthly_budget=excluded.monthly_budget",
        (user_id, payday, monthly_budget)
    )
    conn.commit()
    conn.close()


# ---------- Expenses ----------
def add_expense(user_id: int, amount: float, category: str, date_str: str, description: str = "") -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        (user_id, amount, category.strip(), date_str.strip(), description.strip())
    )
    conn.commit()
    eid = cur.lastrowid
    conn.close()
    return eid


def get_all_expenses(user_id: int) -> List[Tuple]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, user_id, amount, category, date, description FROM expenses WHERE user_id=? ORDER BY date DESC, id DESC",
        (user_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def update_expense(expense_id: int, user_id: int, amount: float, category: str, date_str: str, description: str = "") -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE expenses SET amount=?, category=?, date=?, description=? WHERE id=? AND user_id=?",
        (amount, category.strip(), date_str.strip(), description.strip(), expense_id, user_id)
    )
    conn.commit()
    conn.close()


def delete_expense(expense_id: int, user_id: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=? AND user_id=?", (expense_id, user_id))
    conn.commit()
    conn.close()


# ---------- Cycle math ----------
def _last_day_of_month(y: int, m: int) -> int:
    return _cal.monthrange(y, m)[1]


def _normalize_payday(y: int, m: int, payday: int) -> date:
    """Return the date in (y,m) for the given payday (clamped to last day)."""
    dmax = _last_day_of_month(y, m)
    day = min(max(1, payday), dmax)
    return date(y, m, day)


def get_cycle_bounds(payday: int, ref: Optional[date] = None) -> Tuple[date, date]:
    """
    Return (start_inclusive, end_exclusive) dates for the salary cycle containing `ref`.
    """
    ref = ref or date.today()
    # payday in current month
    current_pd = _normalize_payday(ref.year, ref.month, payday)
    if ref >= current_pd:
        start = current_pd
        # next month
        y, m = (ref.year + 1, 1) if ref.month == 12 else (ref.year, ref.month + 1)
        end = _normalize_payday(y, m, payday)
    else:
        # previous payday
        y, m = (ref.year - 1, 12) if ref.month == 1 else (ref.year, ref.month - 1)
        start = _normalize_payday(y, m, payday)
        end = current_pd
    return start, end


def get_sum_expenses_in_range(user_id: int, start: date, end_excl: date) -> float:
    """
    Sum expenses for [start, end_excl) using ISO dates.
    """
    s, e = start.isoformat(), end_excl.isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id=? AND date >= ? AND date < ?",
        (user_id, s, e)
    )
    total = cur.fetchone()[0] or 0.0
    conn.close()
    return float(total)


def get_cycle_remaining(user_id: int, ref: Optional[date] = None) -> Tuple[float, float, date, date]:
    """
    Return (remaining, spent, start, end_exclusive) for current cycle based on user's settings.
    """
    payday, budget = get_user_settings(user_id)
    start, end = get_cycle_bounds(payday, ref)
    spent = get_sum_expenses_in_range(user_id, start, end)
    remaining = float(budget) - float(spent)
    return remaining, spent, start, end
