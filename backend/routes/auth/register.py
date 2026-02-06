from bcrypt import hashpw, gensalt

from module.db import execute_write, fetch_one
from flask import Blueprint, jsonify, request

from module.crypto import verifier_password

register_bp = Blueprint("register", __name__)



@register_bp.route("/register", methods=["POST"])
def register():
    if not request.json:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400

    name = request.json.get("name")
    prenom = request.json.get("prenom")
    email = request.json.get("email")
    password = request.json.get("password")
    second_password = request.json.get("second_password")

    print(f"Registering user: {name}, {email}, {password}")
    if not name or not email or not password:
        return jsonify({"status": "error"}), 400

    # Vérifier si l'email existe déjà
    existing_user = fetch_one("SELECT id FROM users WHERE email = %s", (email,))
    if existing_user is not None:
        return jsonify({"status": "error", "message": "Cet email est déjà utilisé"}), 409

    # Vérifier que les deux mots de passe correspondent avant le hachage
    if password != second_password:
        return jsonify({"status": "error", "message": "Les mots de passe ne correspondent pas"}), 400

    if not verifier_password(password):
        return jsonify({
            "status": "error", 
            "message": "Le mot de passe doit contenir au minimum 16 caractères, 4 chiffres et 1 caractère spécial"
        }), 401

    # Hash the password with bcrypt
    password_bytes = password.encode("utf-8")
    hash_bytes = hashpw(password_bytes, gensalt())
    hash_str = hash_bytes.decode("utf-8")

    try:
        rowcount, user_id = execute_write(
            "INSERT INTO users (nom, prenom, email, mdp) VALUES (%s, %s, %s, %s)",
            (name, prenom, email, hash_str))
    
        return jsonify({"status": "success", "user_id": user_id}), 200
    except Exception as exc:
        return jsonify({"status": "error", "message": "Erreur lors de l'enregistrement"}), 500
    
