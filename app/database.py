"""SQLite 存储；每次访问使用独立连接。"""
import hashlib
import hmac
import secrets
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

DEMO_USERS = {"alice": "Alice123!", "bob": "Bob123!"}
PASSWORD_ITERATIONS = 200_000


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), PASSWORD_ITERATIONS
    ).hex()


class Database:
    def __init__(self, path):
        self.path = Path(path)

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    expires_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    title TEXT NOT NULL,
                    status TEXT NOT NULL
                );
            """)
            for username, password in DEMO_USERS.items():
                row = connection.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
                if row is None:
                    salt = secrets.token_hex(16)
                    connection.execute(
                        "INSERT INTO users(username, password_hash, salt) VALUES (?, ?, ?)",
                        (username, hash_password(password, salt), salt),
                    )

    def authenticate(self, username, password):
        with self.connect() as connection:
            user = connection.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            if user is None or not hmac.compare_digest(
                user["password_hash"], hash_password(password, user["salt"])
            ):
                return None
            token = secrets.token_urlsafe(32)
            connection.execute("DELETE FROM sessions WHERE expires_at < ?", (time.time(),))
            connection.execute(
                "INSERT INTO sessions VALUES (?, ?, ?)",
                (hashlib.sha256(token.encode()).hexdigest(), user["id"], time.time() + 28_800),
            )
            return token

    def user_for_token(self, token):
        with self.connect() as connection:
            row = connection.execute(
                "SELECT user_id FROM sessions WHERE token_hash = ? AND expires_at > ?",
                (hashlib.sha256(token.encode()).hexdigest(), time.time()),
            ).fetchone()
            return row["user_id"] if row else None

    def create_task(self, user_id, title, status):
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO tasks(user_id, title, status) VALUES (?, ?, ?)", (user_id, title, status)
            )
            return dict(connection.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone())

    def get_task(self, task_id):
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            return dict(row) if row else None

    def update_task(self, task_id, title, status):
        with self.connect() as connection:
            connection.execute("UPDATE tasks SET title = ?, status = ? WHERE id = ?", (title, status, task_id))
            return dict(connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone())

    def delete_task(self, task_id):
        with self.connect() as connection:
            connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
