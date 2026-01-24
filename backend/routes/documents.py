import os
from io import BytesIO

from flask import Blueprint, request, send_file, g

from module.api_retour import api_response
from module.db import execute_write, fetch_all, fetch_one
from module.minio_client import upload_file, download_file, delete_file

documents_bp = Blueprint("documents", __name__)


@documents_bp.route("/documents/upload", methods=["POST"])
def upload_document():
    """
    Upload un document chiffré

    Payload attendu:
    {
        "file_name": "contrat.pdf",
        "file_data": "base64_encrypted_data",
        "dek_encrypted": "base64_wrapped_dek",
        "iv": "base64_iv",
        "sha256": "hash_du_fichier_original"
    }
    """
    user_id = None
    try:
        # Récupérer l'utilisateur depuis g (déjà décodé par le middleware)
        if not g.user:
            return api_response({"status": "error", "message": "Non authentifié"}, 401, None, "Upload failed: not authenticated")
        
        user_id = g.user.get("id")
        if not user_id:
            return api_response({"status": "error", "message": "ID utilisateur manquant"}, 401, None, "Upload failed: missing user ID")

        # Récupérer les données du formulaire
        data = request.get_json()
        if not data:
            return api_response({"status": "error", "message": "Données manquantes"}, 400, user_id, "Upload failed: missing data")

        file_name = data.get("file_name")
        file_data_b64 = data.get("file_data")
        dek_encrypted = data.get("dek_encrypted")
        iv = data.get("iv")
        sha256 = data.get("sha256")

        if not all([file_name, file_data_b64, dek_encrypted, iv, sha256]):
            return api_response({"status": "error", "message": "Paramètres manquants"}, 400, user_id, "Upload failed: missing parameters")

        # Décoder le fichier chiffré depuis base64
        import base64
        file_data = base64.b64decode(file_data_b64)
        file_size = len(file_data)
        _, ext = os.path.splitext(file_name)
        extension = ext[1:].lower() if ext else None

        # Upload vers MinIO (sans métadonnées)
        object_name = upload_file(user_id, file_data, file_name, {})

        try:
            execute_write(
                "INSERT INTO documents (id_users, id_folder, nom_original, extension, taille_octets, object_name, dek_encrypted, iv, sha256) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (user_id, None, file_name, extension, file_size, object_name, dek_encrypted, iv, sha256),
            )
        except Exception:
            try:
                delete_file(user_id, object_name)
            except Exception as cleanup_exc:
                print(f"[ERROR] Cleanup failed: {cleanup_exc}")
            raise

        return api_response({
            "status": "success",
            "data": {
                "message": "Document uploadé avec succès",
                "object_name": object_name,
                "file_name": file_name
            }
        }, 200, user_id, f"Document uploaded: {file_name}")

    except Exception as e:
        print(f"[ERROR] Upload document: {e}")
        return api_response({"status": "error", "message": f"Erreur lors de l'upload: {str(e)}"}, 500, user_id, f"Upload error: {str(e)}")




@documents_bp.route("/documents/list", methods=["GET"])
def list_documents():
    """
    Liste tous les documents de l'utilisateur
    """
    user_id = None
    try:
        # Récupérer l'utilisateur depuis g (déjà décodé par le middleware)
        if not g.user:
            return api_response({"status": "error", "message": "Non authentifié"}, 401, None, "List failed: not authenticated")
        
        user_id = g.user.get("id")
        if not user_id:
            return api_response({"status": "error", "message": "ID utilisateur manquant"}, 401, None, "List failed: missing user ID")

        # Récupérer la liste des documents depuis la base
        rows = fetch_all(
            "SELECT object_name, nom_original, taille_octets, created_at, dek_encrypted, iv, sha256 FROM documents WHERE id_users = %s ORDER BY created_at DESC",
            (user_id,),
        )

        # Formater la réponse
        documents = []
        for row in rows:
            created_at = row.get("created_at")
            if created_at is None:
                last_modified = None
            elif hasattr(created_at, "isoformat"):
                last_modified = created_at.isoformat()
            else:
                last_modified = str(created_at)
            documents.append({
                "object_name": row["object_name"],
                "file_name": row["nom_original"],
                "size": row["taille_octets"],
                "last_modified": last_modified,
                "dek_encrypted": row["dek_encrypted"],
                "iv": row["iv"],
                "sha256": row["sha256"]
            })

        return api_response({
            "status": "success",
            "data": {
                "documents": documents,
                "count": len(documents)
            }
        }, 200, user_id, "Documents listed")

    except Exception as e:
        print(f"[ERROR] List documents: {e}")
        return api_response({"status": "error", "message": f"Erreur lors de la récupération: {str(e)}"}, 500, user_id, f"List error: {str(e)}")


@documents_bp.route("/documents/download/<path:object_name>", methods=["GET"])
def download_document(object_name):
    """
    Télécharge un document chiffré
    """
    try:
        # Récupérer l'utilisateur depuis g (déjà décodé par le middleware)
        user_id = g.user.get("id")

        document = fetch_one(
            "SELECT nom_original, dek_encrypted, iv, sha256 FROM documents WHERE id_users = %s AND object_name = %s",
            (user_id, object_name),
        )
        if document is None:
            return api_response({"status": "error", "message": "Accès non autorisé"}, 403, user_id, "Download denied: document not found")

        # Télécharger le fichier
        file_data, _ = download_file(user_id, object_name)

        # Récupérer le nom original
        original_name = document.get("nom_original", "document")

        # Créer la réponse avec les métadonnées dans les headers
        response = send_file(
            BytesIO(file_data),
            mimetype="application/octet-stream",
            as_attachment=True,
            download_name=original_name
        )

        # Ajouter les métadonnées crypto dans les headers
        response.headers["X-DEK-Encrypted"] = document.get("dek_encrypted", "")
        response.headers["X-IV"] = document.get("iv", "")
        response.headers["X-SHA256"] = document.get("sha256", "")

        return response

    except PermissionError as e:
        return api_response({"status": "error", "message": "Accès non autorisé"}, 403, g.user.get("id"), "Download denied: permission error")
    except Exception as e:
        print(f"[ERROR] Download document: {e}")
        return api_response({"status": "error", "message": f"Erreur lors du téléchargement: {str(e)}"}, 500, g.user.get("id"), f"Download error: {str(e)}")


@documents_bp.route("/documents/delete/<path:object_name>", methods=["DELETE"])
def delete_document(object_name):
    """
    Supprime un document
    """
    try:
        # Récupérer l'utilisateur depuis g (déjà décodé par le middleware)
        user_id = g.user.get("id")

        document = fetch_one(
            "SELECT id FROM documents WHERE id_users = %s AND object_name = %s",
            (user_id, object_name),
        )
        if document is None:
            return api_response({"status": "error", "message": "Accès non autorisé"}, 403, user_id, "Delete denied: document not found")

        # Supprimer le fichier
        delete_file(user_id, object_name)
        execute_write(
            "DELETE FROM documents WHERE id = %s",
            (document["id"],),
        )

        return api_response({
            "status": "success",
            "data": {"message": "Document supprimé avec succès"}
        }, 200, user_id, f"Document deleted: {object_name}")

    except PermissionError as e:
        return api_response({"status": "error", "message": "Accès non autorisé"}, 403, g.user.get("id"), "Delete denied: permission error")
    except Exception as e:
        print(f"[ERROR] Delete document: {e}")
        return api_response({"status": "error", "message": f"Erreur lors de la suppression: {str(e)}"}, 500, g.user.get("id"), f"Delete error: {str(e)}")
