

from db import fetch_one
from flask import Blueprint, jsonify, request
from bcrypt import checkpw
login_bp = Blueprint("login", __name__)


@login_bp.route("/login", methods=["POST"])
def login():
    email = request.json.get("email")
    password = request.json.get("password")

    try :
        mdp = fetch_one("SELECT mdp FROM users WHERE email = %s", (email,))
        if mdp is None:
            return jsonify({"status": "error", "message": "the uemail is not find"}), 404
        

        motdepasse_bytes = password.encode("utf-8")
        hash_bytes = mdp['mdp'].encode("utf-8")
        if not checkpw(motdepasse_bytes, hash_bytes):
            return jsonify({"status": "error", "message": "Invalid password"}), 401
        
        else :
            return jsonify({"status": "success", "message": "Login successful"}), 200
        
    except Exception as exc :
        return jsonify({"status": "error", "message": str(exc)}), 500

