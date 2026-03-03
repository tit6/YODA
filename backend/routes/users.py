from flask import Blueprint, g, request

from module.api_retour import api_response
from module.db import fetch_all


users_bp = Blueprint("users", __name__)


@users_bp.route("/users/list", methods=["GET"])
def list_users():
    """
    Liste les utilisateurs du site (pour partage interne).
    Optionnel: ?q=... pour filtrer (email/nom/prenom).
    """
    user_id = None
    try:
        if not g.user:
            return api_response({"status": "error", "message": "Non authentifié"}, 401, None, "Users list failed: not authenticated")

        user_id = g.user.get("id")
        if not user_id:
            return api_response({"status": "error", "message": "ID utilisateur manquant"}, 401, None, "Users list failed: missing user ID")

        q = (request.args.get("q") or "").strip()
        if q:
            like = f"%{q}%"
            rows = fetch_all(
                "SELECT id, nom, prenom, email FROM users "
                "WHERE id <> %s AND (email LIKE %s OR nom LIKE %s OR prenom LIKE %s) "
                "ORDER BY nom ASC, prenom ASC LIMIT 50",
                (user_id, like, like, like),
            )
        else:
            rows = fetch_all(
                "SELECT id, nom, prenom, email FROM users WHERE id <> %s ORDER BY nom ASC, prenom ASC LIMIT 200",
                (user_id,),
            )

        users = [
            {"id": int(r["id"]), "nom": r.get("nom") or "", "prenom": r.get("prenom") or "", "email": r.get("email") or ""}
            for r in rows
        ]

        return api_response(
            {"status": "success", "data": {"users": users, "count": len(users)}},
            200,
            user_id,
            "Users listed",
        )
    except Exception as exc:
        print(f"[ERROR] List users: {exc}")
        return api_response(
            {"status": "error", "message": f"Erreur lors de la récupération: {str(exc)}"},
            500,
            user_id,
            f"Users list error: {str(exc)}",
        )

