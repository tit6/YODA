from flask import Blueprint, request, g

from module.api_retour import api_response
from module.db import execute_write, fetch_all, fetch_one

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/users", methods=["GET"])
def list_users():
    users = fetch_all(
        """
        SELECT id, nom, prenom, email, is_ban, is_admin
        FROM users
        ORDER BY is_admin DESC, nom ASC, prenom ASC, email ASC
        """
    )
    return api_response({"status": "success", "users": users}, 200, g.user["id"], "Admin listed users")


@admin_bp.route("/admin/toggle-ban", methods=["POST"])
def toggle_user_ban():
    user_id = request.json.get("user_id")
    if not user_id:
        return api_response({"status": "error", "message": "user_id is required"}, 400, g.user["id"], "Admin toggle ban failed: missing user_id")

    user = fetch_one(
        "SELECT id, nom, prenom, email, is_ban FROM users WHERE id = %s",
        (user_id,)
    )
    if user is None:
        return api_response({"status": "error", "message": "User not found"}, 404, g.user["id"], f"Admin toggle ban failed: user {user_id} not found")

    next_status = 0 if int(bool(user.get("is_ban", 0))) == 1 else 1
    rowcount, _ = execute_write(
        "UPDATE users SET is_ban = %s WHERE id = %s",
        (next_status, user_id)
    )
    if rowcount <= 0:
        return api_response({"status": "error", "message": "Failed to update user status"}, 400, g.user["id"], f"Admin toggle ban failed for user {user_id}")

    action = "banned" if next_status == 1 else "unbanned"
    return api_response(
        {
            "status": "success",
            "message": f"User {action} successfully",
            "user": {
                "id": user["id"],
                "nom": user["nom"],
                "prenom": user["prenom"],
                "email": user["email"],
                "is_ban": next_status,
            },
        },
        200,
        g.user["id"],
        f"Admin {action} user {user_id}"
    )
