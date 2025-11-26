from config import SECRET_KEY
from flask import request, jsonify, g
import jwt
from jwt import InvalidTokenError, ExpiredSignatureError

PUBLIC_PATHS = [
    "/api/login",
    "/api/register",
]

def is_public(path: str) -> bool:
    return any(path.startswith(p) for p in PUBLIC_PATHS)

def auth_middleware():
    
    path = request.path
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
    except InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    g.user = payload  # pour utilisation dans les routes
