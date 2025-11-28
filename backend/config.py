import os
import secrets

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

# Configuration MinIO
from minio import Minio

minio_client = Minio(
    os.getenv('MINIO_ENDPOINT') or 'localhost:9000',
    access_key=os.getenv('MINIO_ACCESS_KEY') or '',
    secret_key=os.getenv('MINIO_SECRET_KEY') or '',
    secure=False
)

BUCKET_NAME = 'coffre-fort'

#SECRET_KEY = secrets.token_hex(4096)
SECRET_KEY = "coucou"
