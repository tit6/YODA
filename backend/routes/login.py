from flask import Blueprint, jsonify, request, g
from bcrypt import checkpw

from module.db import fetch_one
from module.jwt_ag import encode_jwt
from module.api_retour import api_response
from routes.a2f import check_a2f_status

login_bp = Blueprint("login", __name__)
name_user = Blueprint("name_user", __name__)

@login_bp.route("/login", methods=["POST"])
def login():
    print("Login route accessed")
    email = request.json.get("email")
    password = request.json.get("password")

    print(f"Logging in user: {email}, {password}")

    try :
        mdp = fetch_one("SELECT id, mdp FROM users WHERE email = %s", (email,))
        if mdp is None:
            return jsonify({"status": "error"}), 200
        

        motdepasse_bytes = password.encode("utf-8")
        hash_bytes = mdp['mdp'].encode("utf-8")
        if not checkpw(motdepasse_bytes, hash_bytes):
            return jsonify({"status": "error"}), 200
        
        else :

            if check_a2f_status(mdp["id"]):
                 token = encode_jwt({"user_id": mdp["id"], "a2f" : 1}, expires_in=3600)
                 message = "Login successful with 2FA wait a2f verification"
            else :
                token = encode_jwt({"user_id": mdp["id"], "a2f" : 0}, expires_in=3600)
                message = "Login successful without 2FA"
            
            return api_response({"status": "success", "token": token}, 200, mdp["id"], message)
                    
    except Exception as exc :
        return jsonify({"status": "error"}), 500

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
