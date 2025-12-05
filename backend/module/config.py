import os
import base64
#import secrets

import pymysql
from dotenv import load_dotenv
from pymysql.cursors import DictCursor

# Make .env variables available everywhere.
load_dotenv()

DATABASE_CONFIG = {
    "host": os.getenv("DATABASE_HOST"),
    "port": int(os.getenv("DATABASE_PORT") or 3306),
    "user": os.getenv("DATABASE_USER"),
    "password": os.getenv("DATABASE_PASSWORD"),
    "database": os.getenv("DATABASE_NAME"),
    "charset": "utf8mb4",
    "cursorclass": DictCursor,
}

#SECRET_KEY = secrets.token_hex(4096)
SECRET_KEY = "coucou"


#AES key for rsa otp in db (base64 in .env → bytes for AES)
def _load_master_key() -> bytes | None:
    raw_key = (os.getenv("APP_MASTER_KEY") or "").strip()
    if not raw_key:
        return None
    try:
        key_bytes = base64.b64decode(raw_key)
    except Exception as exc:
        raise ValueError("APP_MASTER_KEY must be valid base64") from exc
    if len(key_bytes) not in (16, 24, 32):
        raise ValueError(f"APP_MASTER_KEY must decode to 16, 24 or 32 bytes, got {len(key_bytes)}")
    return key_bytes

APP_MASTER_KEY = _load_master_key()
