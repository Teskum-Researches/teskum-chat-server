from config import db_hash_type, pbkdf2_hmac_global_salt
if db_hash_type == "bcrypt":
    import bcrypt
else:
    import hashlib
import secrets
import base64
from db import ChatDB
import os

sessions = {}

def hash_password(password: str, username: str) -> str:
    if db_hash_type == "pbkdf2_hmac":
        salt = pbkdf2_hmac_global_salt + username.encode('utf-8')
        pwd_hash_bytes = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        pwd_hash_bytes_base64 = base64.b64encode(pwd_hash_bytes)
        pwd_hash_str_base64 = pwd_hash_bytes_base64.decode('utf-8')
        #print(pwd_hash_str_base64)
        return pwd_hash_str_base64
    elif db_hash_type == "bcrypt":
        password_bytes = password.encode('utf-8')
        pwd_hash_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        pwd_hash_bytes_base64 = base64.b64encode(pwd_hash_bytes)
        pwd_hash_str_base64 = pwd_hash_bytes_base64.decode('utf-8')
        return pwd_hash_str_base64
    else:
        print("Invalid db_hash_type!")

def check_password(password: str, username: str) -> bool:
    with ChatDB() as db:
        db_pass = db.get_user(username=username)[2]
    if db_hash_type == "pbkdf2":
        usr_pass = hash_password(password=password,username=username)
        if usr_pass == db_pass:
            return True
        else:
            return False
    elif db_hash_type == "bcrypt":
        db_pass = base64.b64decode(db_pass)
        return bcrypt.checkpw(password.encode('utf-8'), db_pass)

def check_session(session:str):
    if sessions[session]:
        return True, sessions[session]
    else:
        return False, None

def login(username: str, password: str):
    global sessions
    status = check_password(password=password, username=username)
    if status:
        session = base64.b64encode(os.urandom(16)).decode('utf-8')
        sessions[session] = username
        return [1,session]
    else:
        return [0, None]