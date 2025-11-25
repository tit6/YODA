import os

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
