import secrets
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, g

from module.db import execute_write, fetch_one
from module.api_retour import api_response
from module.minio_client import upload_file, list_user_files, download_file, delete_file



share = Blueprint("share", __name__)



@share.route("/share/upload", methods=["POST"])
def upload_document_shared():
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
        #email du destinatere
        email = data.get("email")
        time = data.get("time")
        number_of_accesses = data.get("number_of_accesses")



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

        if time is None:
            return api_response({"status": "error", "message": "Durée manquante"}, 400, user_id, "Upload failed: missing time")

        if isinstance(time, (int, float)) or (isinstance(time, str) and time.isdigit()):
            expires_at = datetime.utcnow() + timedelta(hours=int(time))
        else:
            try:
                if isinstance(time, str):
                    time = time.replace("Z", "+00:00")
                expires_at = datetime.fromisoformat(time)
            except (TypeError, ValueError):
                return api_response({"status": "error", "message": "Durée invalide"}, 400, user_id, "Upload failed: invalid time")

        if number_of_accesses == "":
            number_of_accesses = None
        if number_of_accesses is not None:
            try:
                number_of_accesses = int(number_of_accesses)
            except (TypeError, ValueError):
                return api_response({"status": "error", "message": "Nombre d'accès invalide"}, 400, user_id, "Upload failed: invalid max views")

        # Upload vers MinIO
        object_name = upload_file(f"{user_id}_shared", file_data, file_name, metadata)

        token = secrets.token_urlsafe(32)

            
        try:
            rowcount, t = execute_write(
                "INSERT INTO shared_files (name_document, id_owner, token, SEK, destination_email, expires_at, max_views) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (file_name, user_id, token, dek_encrypted, email, expires_at, number_of_accesses))

            return jsonify({"status": "success", "token": token}), 200
        except Exception as exc:
            print(f"[ERROR] Insert shared_files: {exc}")
            return jsonify({"status": "error", "message": str(exc)}), 500


    except Exception as e:
        print(f"[ERROR] Upload document: {e}")
        return api_response({"status": "error", "message": f"Erreur lors de l'upload: {str(e)}"}, 500, user_id, f"Upload error: {str(e)}")




@share.route("/share/list", methods=["GET"])
def list_documents():
    """
    Liste tous les documents de l'utilisateur
    """
    try:
        # Récupérer l'utilisateur depuis g (déjà décodé par le middleware)
        user_id = g.user.get("id")


        # Récupérer la liste des fichiers
        files = list_user_files(f"{user_id}_shared")

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
