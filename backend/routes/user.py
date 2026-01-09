from flask import Blueprint, jsonify, request, g
from bcrypt import checkpw, gensalt, hashpw
from module.db import fetch_one, execute_write
from module.api_retour import api_response
from .auth.a2f import is_password_valid
from module.crypto import verifier_password


name_user = Blueprint("name_user", __name__)
statue_session = Blueprint("statue_session", __name__)
change_password = Blueprint("change_password", __name__)
public_key_bp = Blueprint("public_key", __name__)

@name_user.route("/name_user", methods=["GET"])
def name_users():
    id = g.user["id"]
    try :
        name = fetch_one("SELECT nom, prenom FROM users WHERE id = %s", (id,))
        if name is None:
            return jsonify({"status": "error"}), 200
        else :
            return jsonify({"status": "success", "nom": name["nom"], "prenom": name["prenom"]}), 200
    except Exception as exc :
        return jsonify({"status": "error"}), 500

@statue_session.route("/statue_session", methods=["GET"])
def statue_sessions():
    id = g.user["id"]
    try :
        return api_response({"status": "success"}, 200, id, "Session is valid")
    except Exception as exc :
        return api_response({"status": "error"}, 500, id, "Error checking session status")


@change_password.route("/change_password", methods=["POST"])
def change_passwords():
    id = g.user["id"]
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")
    confirme_password = request.json.get("confirme_password")

    if not old_password or not new_password or not confirme_password:
        return api_response({"status": "error"}, 400, id, "Change password failed: missing fields")

    if confirme_password != new_password:
        return api_response({"status": "error"}, 405, id, "Change password failed: missing fields")

    if verifier_password(new_password):
        return api_response({"status": "error"}, 402, id, "Change password failed: new password too short or not 4 int or special caracter")

    mdp = fetch_one("SELECT mdp FROM users WHERE id = %s", (id,))
    if mdp is None:
        return api_response({"status": "error"}, 404, id, "Change password failed: user not found")
    if not is_password_valid(old_password, mdp["mdp"]):
        return api_response({"status": "error"}, 401, id, "Change password failed: incorrect old password")
    
    #He egal
    if is_password_valid(new_password, mdp["mdp"]):
        return api_response({"status": "error"}, 404, id, "Change password failed: new password matches old password")
    
    salt = gensalt()
    new_hash_bytes = hashpw(new_password.encode("utf-8"), salt)
    new_hash_str = new_hash_bytes.decode("utf-8")


    rowcount, _ = execute_write(
        "UPDATE users SET mdp = %s WHERE id = %s",
        (new_hash_str, id)
    )
    if rowcount == 0:
        return api_response({"status": "error"}, 500, id, "Change password failed: database error")

    return api_response({"status": "success"}, 200, id, "Password changed successfully")


@public_key_bp.route("/user/public-key", methods=["GET"])
def get_public_key():
    """Récupère la clé publique RSA de l'utilisateur"""
    user_id = g.user["id"]
    try:
        result = fetch_one("SELECT public_key FROM users WHERE id = %s", (user_id,))
        if result is None or result.get("public_key") is None:
            return api_response({"status": "error"}, 404, user_id, "Public key not found")

        return api_response({
            "status": "success",
            "data": {"public_key": result["public_key"]}
        }, 200, user_id, "Public key retrieved")

    except Exception as exc:
        return api_response({"status": "error"}, 500, user_id, f"Error retrieving public key: {exc}")


@public_key_bp.route("/user/public-key", methods=["POST"])
def save_public_key():
    """Sauvegarde la clé publique RSA de l'utilisateur"""
    user_id = g.user["id"]
    try:
        public_key = request.json.get("public_key")
        if not public_key:
            return api_response({"status": "error"}, 400, user_id, "Public key is required")

        # Vérifier si l'utilisateur a déjà une clé publique
        existing = fetch_one("SELECT public_key FROM users WHERE id = %s", (user_id,))
        if existing and existing.get("public_key"):
            return api_response({"status": "error"}, 409, user_id, "Public key already exists")

        # Sauvegarder la clé publique
        rowcount, _ = execute_write(
            "UPDATE users SET public_key = %s WHERE id = %s",
            (public_key, user_id)
        )

        if rowcount == 0:
            return api_response({"status": "error"}, 500, user_id, "Failed to save public key")

        return api_response({"status": "success"}, 200, user_id, "Public key saved")

    except Exception as exc:
        return api_response({"status": "error"}, 500, user_id, f"Error saving public key: {exc}")


