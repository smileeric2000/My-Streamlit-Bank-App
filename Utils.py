
#Utils.py 
#Database handler


import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List

DB_PATH = Path(__file__).parent / "database.db"

def init_db(db_path: Optional[str] = None):
    """Initialize the SQLite database (create tables if they don't exist)."""
    path = DB_PATH if db_path is None else Path(db_path)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    #users table
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        account_num INTEGER PRIMARY KEY,
        account_name TEXT NOT NULL,
        account_balance REAL NOT NULL DEFAULT 0,
        account_password TEXT NOT NULL
    )""")
    #transactions table
    cur.execute("""CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_num INTEGER NOT NULL,
        direction TEXT NOT NULL,
        amount REAL NOT NULL,
        note TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY(account_num) REFERENCES users(account_num)
    );""")
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def create_user(account_num: int, account_name: str, account_password: str, initial_balance: float = 0.0) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (account_num, account_name, account_balance, account_password) VALUES (?,?,?,?)",
                    (account_num, account_name, float(initial_balance), str(account_password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def update_profile_img(account_num, img_base64):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET profile_img = ? WHERE account_num = ?",
        (img_base64, account_num)
    )
    conn.commit()
    conn.close()


def get_user(account_num: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT account_num, account_name, account_balance, account_password, profile_img FROM users WHERE account_num = ?", (account_num,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return dict(account_num=row[0], account_name=row[1], account_balance=row[2], account_password=row[3], profile_img =row[4])

def authenticate(account_num: int, password: str) -> Optional[Dict[str, Any]]:
    user = get_user(account_num)
    if user and str(password) == str(user["account_password"]):
        return user
    return None

def update_balance(account_num: int, new_balance: float):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET account_balance = ? WHERE account_num = ?", (float(new_balance), account_num))
    conn.commit()
    conn.close()

def add_transaction(account_num: int, direction: str, amount: float, note: str = None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO transactions (account_num, direction, amount, note) VALUES (?,?,?,?)",
                (account_num, direction, float(amount), note))
    conn.commit()
    conn.close()

def get_transactions(account_num: int, limit: int = 10) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, direction, amount, note, created_at FROM transactions WHERE account_num = ? ORDER BY id DESC LIMIT ?", (account_num, limit))
    rows = cur.fetchall()
    conn.close()
    return [dict(id=r[0], direction=r[1], amount=r[2], note=r[3], created_at=r[4]) for r in rows]

def transfer(sender_acc: int, receiver_acc: int, amount: float, note: str = None) -> bool:
   
    if amount <= 0:
        return False

    conn = get_connection()
    cur = conn.cursor()

    try:
        #Fetch sender and receiver
        cur.execute("SELECT account_balance FROM users WHERE account_num = ?", (sender_acc,))
        sender_row = cur.fetchone()

        cur.execute("SELECT account_balance FROM users WHERE account_num = ?", (receiver_acc,))
        receiver_row = cur.fetchone()

        #Validate accounts
        if not sender_row or not receiver_row:
            return False

        sender_balance = sender_row[0]
        receiver_balance = receiver_row[0]

        #Ensure sender has enough money
        if sender_balance < amount:
            return False

        #Begin atomic transaction
        conn.execute("BEGIN TRANSACTION")

        #Deduct from sender
        new_sender_balance = sender_balance - amount
        cur.execute("UPDATE users SET account_balance=? WHERE account_num=?", 
                    (new_sender_balance, sender_acc))

        #Add to receiver
        new_receiver_balance = receiver_balance + amount
        cur.execute("UPDATE users SET account_balance=? WHERE account_num=?", 
                    (new_receiver_balance, receiver_acc))

        #Log sender transaction
        cur.execute(
            "INSERT INTO transactions (account_num, direction, amount, note) VALUES (?,?,?,?)",
            (sender_acc, "debit", amount, note or f"Transfer to {receiver_acc}")
        )

        #Log recipient transaction
        cur.execute(
            "INSERT INTO transactions (account_num, direction, amount, note) VALUES (?,?,?,?)",
            (receiver_acc, "credit", amount, note or f"Transfer from {sender_acc}")
        )

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        return False

    finally:
        conn.close()
