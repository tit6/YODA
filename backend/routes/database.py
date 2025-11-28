from flask import Blueprint, jsonify

from module.db import fetch_all, fetch_one

database_bp = Blueprint("database", __name__)


@database_bp.route("/db-test")
def db_test():
    try:
        version = fetch_one("SELECT VERSION()")
        tables = fetch_all("SHOW TABLES")
        tables_list = [next(iter(row.values())) for row in tables]

        return jsonify(
            {
                "status": "success",
                "mysql_version": version,
                "tables": tables_list,
            }
        )
    except Exception as exc:
        return jsonify({"status": "error"}), 500
