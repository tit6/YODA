from flask import Blueprint, request, jsonify, send_file, g
from module.minio_client import upload_file, list_user_files, download_file, delete_file
from module.api_retour import api_response
from io import BytesIO

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
    try:
        # Récupérer l'utilisateur depuis g (déjà décodé par le middleware)
        user_id = g.user.get("id")

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

        # Métadonnées à stocker avec le fichier
        metadata = {
            "dek-encrypted": dek_encrypted,
            "iv": iv,
            "sha256": sha256,
            "original-name": file_name
        }

        # Upload vers MinIO
        object_name = upload_file(user_id, file_data, file_name, metadata)

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
    try:
        # Récupérer l'utilisateur depuis g (déjà décodé par le middleware)
        user_id = g.user.get("id")

        # Récupérer la liste des fichiers
        files = list_user_files(user_id)

        # Formater la réponse
        documents = []
        for file in files:
            # Extraire le nom original depuis les métadonnées
            original_name = file["metadata"].get("x-amz-meta-original-name", file["file_name"])

            documents.append({
                "object_name": file["object_name"],
                "file_name": original_name,
                "size": file["size"],
                "last_modified": file["last_modified"],
                "dek_encrypted": file["metadata"].get("x-amz-meta-dek-encrypted"),
                "iv": file["metadata"].get("x-amz-meta-iv"),
                "sha256": file["metadata"].get("x-amz-meta-sha256")
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

        # Télécharger le fichier
        file_data, metadata = download_file(user_id, object_name)

        # Récupérer le nom original
        original_name = metadata.get("x-amz-meta-original-name", "document")

        # Créer la réponse avec les métadonnées dans les headers
        response = send_file(
            BytesIO(file_data),
            mimetype="application/octet-stream",
            as_attachment=True,
            download_name=original_name
        )

        # Ajouter les métadonnées crypto dans les headers
        response.headers["X-DEK-Encrypted"] = metadata.get("x-amz-meta-dek-encrypted", "")
        response.headers["X-IV"] = metadata.get("x-amz-meta-iv", "")
        response.headers["X-SHA256"] = metadata.get("x-amz-meta-sha256", "")

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

        # Supprimer le fichier
        delete_file(user_id, object_name)

        return api_response({
            "status": "success",
            "data": {"message": "Document supprimé avec succès"}
        }, 200, user_id, f"Document deleted: {object_name}")

    except PermissionError as e:
        return api_response({"status": "error", "message": "Accès non autorisé"}, 403, g.user.get("id"), "Delete denied: permission error")
    except Exception as e:
        print(f"[ERROR] Delete document: {e}")
        return api_response({"status": "error", "message": f"Erreur lors de la suppression: {str(e)}"}, 500, g.user.get("id"), f"Delete error: {str(e)}")
