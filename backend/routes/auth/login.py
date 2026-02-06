from flask import Blueprint, jsonify, request, g
from bcrypt import checkpw

from module.db import fetch_one, execute_write
from module.jwt_ag import encode_jwt
from module.api_retour import api_response
from routes.auth.a2f import check_a2f_status
from datetime import datetime, timedelta

login_bp = Blueprint("login", __name__)


@login_bp.route("/login", methods=["POST"])
def login():

    banned_ip = fetch_one("SELECT attempts, last_attempt FROM failed_login_attempts WHERE ip = %s", (request.remote_addr,))

    if banned_ip and banned_ip["attempts"] >= 5:
        if banned_ip["last_attempt"] < datetime.now() - timedelta(minutes=5):
            execute_write("DELETE FROM failed_login_attempts WHERE ip = %s", (request.remote_addr,))
        else:
            return jsonify({"status": "error"}), 403

    email = request.json.get("email")
    password = request.json.get("password")

    try :
        mdp = fetch_one("SELECT id, mdp FROM users WHERE email = %s", (email,))
        if mdp is None:
            return jsonify({"status": "error"}), 403
        

        motdepasse_bytes = password.encode("utf-8")
        hash_bytes = mdp['mdp'].encode("utf-8")
        if not checkpw(motdepasse_bytes, hash_bytes):

            existing = fetch_one("SELECT attempts FROM failed_login_attempts WHERE ip = %s", (request.remote_addr,))
            if existing:
                execute_write("UPDATE failed_login_attempts SET attempts = attempts + 1 WHERE ip = %s",
                              (request.remote_addr,))
            else:
                execute_write("INSERT INTO failed_login_attempts (ip, attempts) VALUES (%s, %s)",
                              (request.remote_addr, 1))
            return jsonify({"status": "error"}), 403
        
        else :

            existing = fetch_one("SELECT attempts FROM failed_login_attempts WHERE ip = %s", (request.remote_addr,))
            if existing:
                execute_write("DELETE FROM failed_login_attempts WHERE ip = %s", (request.remote_addr,))

            if check_a2f_status(mdp["id"]) == 2:
                 token = encode_jwt({"id": mdp["id"], "a2f" : 1}, expires_in=3600)
                 message = "Login successful with 2FA wait a2f verification"
            else :
                token = encode_jwt({"id": mdp["id"], "a2f" : 0}, expires_in=3600)
                message = "Login successful without 2FA"
            
            return api_response({"status": "success", "token": token}, 200, mdp["id"], message)
                    
    except Exception as exc :
        print(exc)
        return jsonify({"status": "error"}), 500
