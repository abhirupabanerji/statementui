import sqlite3
import bcrypt
from database import create_connection


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def check_password(password, hashed):

    if isinstance(hashed, str):
        hashed = hashed.encode()

    return bcrypt.checkpw(password.encode(), hashed)


def login_user(username, password):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM users WHERE username=?",
        (username,)
    )

    data = cursor.fetchone()
    conn.close()

    if data:
        return check_password(password, data[0])

    return False


def register_user(username, password):

    conn = create_connection()
    cursor = conn.cursor()

    hashed = hash_password(password).decode()

    try:
        cursor.execute(
            "INSERT INTO users(username, password) VALUES (?, ?)",
            (username, hashed)
        )
        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False