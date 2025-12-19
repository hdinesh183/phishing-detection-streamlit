import sqlite3
import bcrypt
import re

DB_NAME = "db.sqlite3"

# ---------------- DB CONNECTION ----------------
def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

# ---------------- CREATE TABLE ----------------
def create_users_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password BLOB NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ---------------- EMAIL VALIDATION ----------------
def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email)

# ---------------- REGISTER USER ----------------
def register_user(username, email, password, confirm_password):
    if not username or not email or not password or not confirm_password:
        return False, "All fields are required"

    if password != confirm_password:
        return False, "Passwords do not match"

    if len(password) < 6:
        return False, "Password must be at least 6 characters"

    if not is_valid_email(email):
        return False, "Invalid email format"

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed_pw)
        )
        conn.commit()
        conn.close()
        return True, "Registration successful"
    except sqlite3.IntegrityError:
        return False, "Username or Email already exists"

# ---------------- LOGIN USER ----------------
def login_user(identifier, password):
    conn = get_connection()
    cur = conn.cursor()

    # Allow login using username OR email
    cur.execute(
        "SELECT password FROM users WHERE username = ? OR email = ?",
        (identifier, identifier)
    )
    result = cur.fetchone()
    conn.close()

    if result and bcrypt.checkpw(password.encode(), result[0]):
        return True
    return False
