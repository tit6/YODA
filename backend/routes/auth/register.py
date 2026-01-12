from bcrypt import hashpw, gensalt

from module.db import execute_write
from flask import Blueprint, jsonify, request

from module.crypto import verifier_password

register_bp = Blueprint("register", __name__)



@register_bp.route("/register", methods=["POST"])
def register():

    name = request.json.get("name")
    prenom = request.json.get("prenom")
    email = request.json.get("email")
    password = request.json.get("password")
    second_password = request.json.get("second_password")

    print(f"Registering user: {name}, {email}, {password}")
    if not name or not email or not password:
        return jsonify({"status": "error"}), 400


    #bcrypt wait the bytes
    motdepasse_bytes = password.encode("utf-8")
    second_password_bytes = second_password.encode("utf-8")

    salt = gensalt()
    # generate salt and hash
    hash_bytes = hashpw(motdepasse_bytes, salt)
    second_hash_bytes = hashpw(second_password_bytes, salt)

    # save in utf8 and check password
    hash_str = hash_bytes.decode("utf-8")
    second_hash_str = second_hash_bytes.decode("utf-8")

    if hash_str != second_hash_str:
        return jsonify({"status": "error", "message": "Les mots de passe ne correspondent pas"}), 400
    
    if not verifier_password(password):
        return jsonify({
            "status": "error", 
            "message": "Le mot de passe doit contenir au minimum 16 caractères, 4 chiffres et 1 caractère spécial"
        }), 401

    try:
        rowcount, user_id = execute_write(
            "INSERT INTO users (nom, prenom, email, mdp) VALUES (%s, %s, %s, %s)",
            (name, prenom, email, hash_str))
    
        return jsonify({"status": "success", "user_id": user_id}), 200
    except Exception as exc:
        return jsonify({"status": "error", "message": "Erreur lors de l'enregistrement"}), 500
    
