from bcrypt import hashpw, gensalt

from module.db import execute_write
from flask import Blueprint, jsonify, request

register_bp = Blueprint("register", __name__)



@register_bp.route("/register", methods=["POST"])
def register():

    name = request.json.get("name")
    prenom = request.json.get("prenom")
    email = request.json.get("email")
    password = request.json.get("password")

    print(f"Registering user: {name}, {email}, {password}")
    if not name or not email or not password:
        return jsonify({"status": "error"}), 400

    #bcrypt wait the bytes
    motdepasse_bytes = password.encode("utf-8")

    # generate salt and hash
    hash_bytes = hashpw(motdepasse_bytes, gensalt())

    # save in utf8
    hash_str = hash_bytes.decode("utf-8")

    try:
        rowcount, user_id = execute_write(
            "INSERT INTO users (nom, prenom, email, mdp) VALUES (%s, %s, %s, %s)",
            (name, prenom, email, hash_str))
    
        return jsonify({"status": "success", "user_id": user_id}), 200
    except Exception as exc:
        return jsonify({"status": "error"}), 500
    
