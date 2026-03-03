from flask import Blueprint, jsonify, g
from module.db import fetch_all, fetch_one, execute_write
from module.api_retour import api_response

admin_bp = Blueprint("admin", __name__)


def require_admin():
    """Vérifie que l'utilisateur courant est admin. Retourne une réponse d'erreur si non."""
    if not g.user:
        return jsonify({"status": "error", "message": "Non authentifié"}), 401
    if not g.user.get("is_admin"):
        return jsonify({"status": "error", "message": "Accès refusé"}), 403
    return None


@admin_bp.route("/admin/users", methods=["GET"])
def list_users():
    """Liste tous les utilisateurs (admin uniquement)."""
    err = require_admin()
    if err:
        return err

    user_id = g.user["id"]
    try:
        users = fetch_all(
            "SELECT id, nom, prenom, email, is_admin, is_active FROM users ORDER BY id"
        )
        return api_response(
            {"status": "success", "data": users},
            200,
            user_id,
            "Admin listed users",
        )
    except Exception as exc:
        return api_response(
            {"status": "error", "message": str(exc)},
            500,
            user_id,
            f"Admin list users error: {exc}",
        )


@admin_bp.route("/admin/users/<int:target_id>/toggle-active", methods=["POST"])
def toggle_active(target_id):
    """Active ou désactive un utilisateur (admin uniquement)."""
    err = require_admin()
    if err:
        return err

    user_id = g.user["id"]
    try:
        target = fetch_one("SELECT id, is_active FROM users WHERE id = %s", (target_id,))
        if target is None:
            return api_response(
                {"status": "error", "message": "Utilisateur introuvable"},
                404,
                user_id,
                f"Admin toggle active: user {target_id} not found",
            )

        new_status = 0 if target["is_active"] else 1
        execute_write(
            "UPDATE users SET is_active = %s WHERE id = %s", (new_status, target_id)
        )

        return api_response(
            {"status": "success", "is_active": new_status},
            200,
            user_id,
            f"Admin toggled user {target_id} active to {new_status}",
        )
    except Exception as exc:
        return api_response(
            {"status": "error", "message": str(exc)},
            500,
            user_id,
            f"Admin toggle active error: {exc}",
        )
