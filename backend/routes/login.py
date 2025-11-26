

from db import fetch_one
from flask import Blueprint, jsonify, request
import jwt
from datetime import datetime, timezone, timedelta
from bcrypt import checkpw
from config import SECRET_KEY
login_bp = Blueprint("login", __name__)


@login_bp.route("/login", methods=["POST"])
def login():
    print("Login route accessed")
    email = request.json.get("email")
    password = request.json.get("password")

    print(f"Logging in user: {email}, {password}")

    try :
        mdp = fetch_one("SELECT id, mdp FROM users WHERE email = %s", (email,))
        if mdp is None:
            return jsonify({"status": "error", "message": "the uemail is not find"}), 404
        

        motdepasse_bytes = password.encode("utf-8")
        hash_bytes = mdp['mdp'].encode("utf-8")
        if not checkpw(motdepasse_bytes, hash_bytes):
            return jsonify({"status": "error", "message": "Invalid password"}), 401
        
        else :
            token = jwt.encode({'id': mdp['id'], 'exp': datetime.now(timezone.utc) + timedelta(hours=1)},
                           SECRET_KEY, algorithm="HS256")   

            return jsonify({"status": "success", "message": "Login successful", "token": token}), 200

        
    except Exception as exc :
        return jsonify({"status": "error", "message": str(exc)}), 500

