#!/usr/bin/env python3
from config import db_name, db_encryption_key
import sqlite3
import os
import base64

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError as exc:
    raise ImportError(
        "Package 'cryptography' is required for DB encryption. Install it with: pip install cryptography"
    ) from exc

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, db_name)


def _get_cipher() -> Fernet:
    """Возвращает объект Fernet на основе ключа из config.py/ENV."""
    key_value = db_encryption_key.strip() if db_encryption_key else ""

    if not key_value:
        # Фолбэк для локальной разработки, чтобы сервер стартовал без ENV.
        # Ключ детерминированный, но хранится в коде — это не для production.
        key_value = base64.urlsafe_b64encode(
            b"0123456789abcdef0123456789abcdef"
        ).decode("utf-8")

    key = key_value.encode("utf-8")
    return Fernet(key)


CIPHER = _get_cipher()


class ChatDB:
    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.connection.commit()

    def _encrypt_message(self, text: str) -> str:
        encrypted = CIPHER.encrypt(text.encode("utf-8"))
        return encrypted.decode("utf-8")

    def _decrypt_message(self, encrypted_text: str) -> str:
        try:
            decrypted = CIPHER.decrypt(encrypted_text.encode("utf-8"))
            return decrypted.decode("utf-8")
        except InvalidToken:
            # Поддержка старых записей, если в БД был plaintext.
            return encrypted_text

    def get_messages(self):
        self.cursor.execute('SELECT author, content FROM messages')
        output = self.cursor.fetchall()
        messages = []
        for row in output:
            messages.append({"user": row[0], "content": self._decrypt_message(row[1])})
        return messages

    def add_message(self, user: str, text: str) -> None:
        encrypted_text = self._encrypt_message(text)
        self.cursor.execute(
            "INSERT INTO messages (author, content) VALUES (?, ?)",
            (user, encrypted_text)
        )
        self.connection.commit()

    def add_user(self, username: str, password: str) -> bool:
        self.cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        if self.cursor.fetchone() is not None:
            return False

        self.cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        self.connection.commit()
        return True

    def get_user(self, username):
        self.cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        row = self.cursor.fetchone()
        return row

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
