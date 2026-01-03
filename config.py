#! /usr/bin/env python3
port = 8765
is_secure = False
cert_file = "cert.crt"
cert_key = "cert.key"
is_local = True
host = "0.0.0.0" # Ignored when is_local = True
db_name = "chat.db"
db_hash_type = "bcrypt" # bcrypt or pbkdf2_hmac
pbkdf2_hmac_global_salt = b"JP=ds=9akkeizgfiopseaa223432fsd2026"
