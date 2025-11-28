from flask import Blueprint, jsonify, request, g
from bcrypt import checkpw
from module.db import fetch_one
from module.api_retour import api_response

name_user = Blueprint("name_user", __name__)
statue_session = Blueprint("statue_session", __name__)

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


