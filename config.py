#! /usr/bin/env python3
import os

port = 8765
is_secure = False
cert_file = "cert.crt"
cert_key = "cert.key"
is_local = True
host = "0.0.0.0" # Ignored when is_local = True
db_name = "chat.db"
db_hash_type = "bcrypt" # bcrypt or pbkdf2_hmac
pbkdf2_hmac_global_salt = b"JP=ds=9akkeizgfiopseaa223432fsd2026"

# Шифрование сообщений в БД (AES-256 GCM через Fernet).
# Для production лучше передавать ключ через переменную окружения.
db_encryption_key = os.getenv("CHAT_DB_ENCRYPTION_KEY", "")

# Запретить чувствительные команды по незащищенному ws://
require_secure_transport_for_sensitive_commands = True
