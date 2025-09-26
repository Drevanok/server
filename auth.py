import sqlite3
from database import get_connection

def register_user(username: str, password: str) -> bool:
    try:
        conn = get_connection()
        with conn:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate(username: str, password: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    return row is not None and row[0] == password
