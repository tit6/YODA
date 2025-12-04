from contextlib import closing

import pymysql

from .config import DATABASE_CONFIG


def get_db_connection():
    """Create a database connection using environment settings."""
    return pymysql.connect(**DATABASE_CONFIG)


def fetch_one(query, params=None):
    """Run a query and return a single row."""
    with closing(get_db_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()


def execute_write(query, params=None):
    """Run an INSERT/UPDATE/DELETE and commit."""
    with closing(get_db_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            connection.commit()
            return cursor.rowcount, cursor.lastrowid


def fetch_all(query, params=None):
    """Run a query and return all rows."""
    with closing(get_db_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()

def update_logs(user_id: int = 0, statut: int = 0, action: str = "") -> None:
    """Insert Users_logs in logs table."""
    query = "INSERT INTO logs (id_users, statut, action) VALUES (%s, %s, %s)"
    params = (user_id, statut, action)

    return execute_write(query, params)


    
