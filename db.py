#!/usr/bin/env python3
from config import db_name, db_hash_type, pbkdf2_hmac_global_salt
import sqlite3
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, db_name)


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

    def get_messages(self):
        self.cursor.execute('SELECT author, content FROM messages')
        output = self.cursor.fetchall()
        messages = []
        for row in output:
            messages.append({"user": row[0], "content": row[1]})
        return messages

    def add_message(self, user: str, text: str) -> None:
        self.cursor.execute(
            "INSERT INTO messages (author, content) VALUES (?, ?)",
            (user, text)
        )
        self.connection.commit()
    
    def add_user(self, username: str, password: str) -> bool:
        self.cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        if self.cursor.fetchone() is not None:
            return False  

        password_hash_str = password

        self.cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password_hash_str)
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
