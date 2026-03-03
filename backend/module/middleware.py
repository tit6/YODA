from flask import request, jsonify, g
import jwt
from jwt import ExpiredSignatureError, DecodeError
from .config import SECRET_KEY
from .db import fetch_one


PUBLIC_PATHS = [
    "/api/login",
    "/api/register",
    "/api/validate_a2f",
    "/api/docs",
    "/api/health",
    "/api/db-test",
    "/static",
    "/api/share/name_file",
    "/api/share/download",
]

TEMP_PATHS = [
    "/api/check_a2f",
    "/api/a2f_login",
]

ADMIN_PATHS = [
    "/api/admin",
]


def is_public(path: str) -> bool:
    return any(path.startswith(p) for p in PUBLIC_PATHS)


def is_admin(path: str) -> bool:
    return any(path.startswith(p) for p in ADMIN_PATHS)


def get_user_admin_flag(user_id: int) -> int:
    user = fetch_one("SELECT is_admin FROM users WHERE id = %s", (user_id,))
    if user is None:
        return 0
    return int(bool(user.get("is_admin", 0)))


def auth_middleware():
    path = request.path
    g.user = None  # Initialiser g.user par défaut

    if is_public(path):
        return  # route non protégée

    # Récupération du header Authorization
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    token = auth_header.split(" ", 1)[1].strip()

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except DecodeError:
        return jsonify({"error": "Invalid token"}), 401

    if payload.get("a2f") == 1 and path not in TEMP_PATHS:
        return jsonify({"error": "Invalid token payload"}), 402

    user_id = payload.get("id")
    if user_id is None:
        return jsonify({"error": "Invalid token payload"}), 401

    admin_flag = get_user_admin_flag(user_id)
    payload["admin"] = admin_flag
    payload["is_admin"] = admin_flag

    if is_admin(path) and payload["is_admin"] != 1:
        return jsonify({"error": "Admin access required"}), 403

    g.user = payload  # pour utilisation dans les routes
