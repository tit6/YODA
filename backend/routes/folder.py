from flask import Blueprint, g, request

from module.api_retour import api_response
from module.db import execute_write, fetch_all
from module.folder import create_folder as create_folder_db
from module.folder import get_descendant_folder_ids, get_folder
from module.minio_client import delete_file


folder_bp = Blueprint("folders", __name__)


@folder_bp.route("/documents/folders/create", methods=["POST"])
def create_folder_route():
    user_id = None
    try:
        if not g.user:
            return api_response(
                {"status": "error", "message": "Non authentifié"},
                401,
                None,
                "Folder create failed: not authenticated",
            )

        user_id = g.user.get("id")
        if not user_id:
            return api_response(
                {"status": "error", "message": "ID utilisateur manquant"},
                401,
                None,
                "Folder create failed: missing user ID",
            )

        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()
        parent_id_raw = data.get("parent_id")

        parent_id = None
        if parent_id_raw not in (None, "", 0, "0", "null", "root"):
            try:
                parent_id = int(parent_id_raw)
            except (TypeError, ValueError):
                return api_response(
                    {"status": "error", "message": "parent_id invalide"},
                    400,
                    user_id,
                    "Folder create failed: invalid parent_id",
                )

        try:
            folder_id = create_folder_db(int(user_id), name, parent_id)
        except ValueError as ve:
            return api_response(
                {"status": "error", "message": str(ve)},
                400,
                user_id,
                "Folder create failed: invalid name",
            )
        except PermissionError:
            return api_response(
                {"status": "error", "message": "Parent introuvable ou non autorisé"},
                403,
                user_id,
                "Folder create denied: invalid parent",
            )

        return api_response(
            {
                "status": "success",
                "data": {
                    "folder": {
                        "id": folder_id,
                        "name": name,
                        "parent_id": parent_id,
                    }
                },
            },
            200,
            user_id,
            f"Folder created: {folder_id}",
        )
    except Exception as e:
        print(f"[ERROR] Folder create: {e}")
        return api_response(
            {"status": "error", "message": f"Erreur lors de la création: {str(e)}"},
            500,
            user_id,
            f"Folder create error: {str(e)}",
        )


@folder_bp.route("/documents/folders/delete/<int:folder_id>", methods=["DELETE"])
def delete_folder_route(folder_id: int):
    user_id = None
    try:
        if not g.user:
            return api_response(
                {"status": "error", "message": "Non authentifié"},
                401,
                None,
                "Folder delete failed: not authenticated",
            )

        user_id = g.user.get("id")
        if not user_id:
            return api_response(
                {"status": "error", "message": "ID utilisateur manquant"},
                401,
                None,
                "Folder delete failed: missing user ID",
            )

        # Ownership check (anti "saut" sur les autres users)
        if get_folder(int(user_id), int(folder_id)) is None:
            return api_response(
                {"status": "error", "message": "Dossier introuvable"},
                404,
                user_id,
                "Folder delete failed: not found",
            )

        folder_ids = get_descendant_folder_ids(int(user_id), int(folder_id), include_self=True)
        placeholders = ", ".join(["%s"] * len(folder_ids))

        doc_rows = fetch_all(
            f"SELECT object_name FROM documents WHERE id_users = %s AND id_folder IN ({placeholders})",
            tuple([int(user_id)] + folder_ids),
        )

        # DB first: avoid broken downloads. MinIO cleanup is best-effort.
        execute_write(
            f"DELETE FROM documents WHERE id_users = %s AND id_folder IN ({placeholders})",
            tuple([int(user_id)] + folder_ids),
        )

        execute_write(
            "DELETE FROM folders WHERE id_users = %s AND id = %s",
            (int(user_id), int(folder_id)),
        )

        for d in doc_rows:
            object_name = d.get("object_name")
            if not object_name:
                continue
            try:
                delete_file(int(user_id), object_name)
            except Exception as exc:
                print(f"[WARNING] MinIO delete failed for {object_name}: {exc}")

        return api_response(
            {"status": "success", "data": {"message": "Dossier supprimé"}},
            200,
            user_id,
            f"Folder deleted: {folder_id}",
        )
    except Exception as e:
        print(f"[ERROR] Folder delete: {e}")
        return api_response(
            {"status": "error", "message": f"Erreur lors de la suppression: {str(e)}"},
            500,
            user_id,
            f"Folder delete error: {str(e)}",
        )

'''
CREATE TABLE `folders` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `id_users` INT NOT NULL,
  `nom` VARCHAR(255) NOT NULL,
  `parent_id` INT DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_folders_user` (`id_users`),
  KEY `idx_folders_parent` (`parent_id`),
  CONSTRAINT `fk_folders_users`
    FOREIGN KEY (`id_users`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_folders_parent`
    FOREIGN KEY (`parent_id`) REFERENCES `folders` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

'''
