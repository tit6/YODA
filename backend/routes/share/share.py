from io import BytesIO
import secrets
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, g, send_file
import base64

from module.db import execute_write, fetch_all, fetch_one
from module.api_retour import api_response
from module.minio_client import upload_file, delete_file, download_file



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
        source_object_name = data.get("source_object_name")



        if not all([file_name, file_data_b64, dek_encrypted, iv, sha256]):
            return api_response({"status": "error", "message": "Paramètres manquants"}, 400, user_id, "Upload failed: missing parameters")

        # Décoder le fichier chiffré depuis base64
        import base64
        file_data = base64.b64decode(file_data_b64)

        file_size = len(file_data)

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
        object_name = upload_file(f"{user_id}_shared", file_data, file_name, {})

        token = secrets.token_urlsafe(32)

        document_id = None
        if source_object_name:
            document_row = fetch_one(
                "SELECT id FROM documents WHERE id_users = %s AND object_name = %s",
                (user_id, source_object_name),
            )
            if document_row is None:
                return api_response({"status": "error", "message": "Accès non autorisé"}, 403, user_id, "Share upload denied: document not found")
            document_id = document_row["id"]

            
        try:
            rowcount, t = execute_write(
                "INSERT INTO shared_files (name_document, id_owner, id_document, object_name, taille_octets, token, SEK, iv, sha256, destination_email, expires_at, max_views) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (file_name, user_id, document_id, object_name, file_size, token, dek_encrypted, iv, sha256, email, expires_at, number_of_accesses))

            return jsonify({"status": "success", "token": token}), 200
        except Exception as exc:
            try:
                delete_file(f"{user_id}_shared", object_name)
            except Exception as cleanup_exc:
                print(f"[ERROR] Cleanup failed: {cleanup_exc}")
            print(f"[ERROR] Insert shared_files: {exc}")
            return jsonify({"status": "error", "message": str(exc)}), 500


    except Exception as e:
        print(f"[ERROR] Upload document: {e}")
        return api_response({"status": "error", "message": f"Erreur lors de l'upload: {str(e)}"}, 500, user_id, f"Upload error: {str(e)}")




@share.route("/share/list", methods=["GET"])
def list_documents():
    """
    Liste tous les documents partager de l'utilisateur
    """
    try:
        # Récupérer l'utilisateur depuis g (déjà décodé par le middleware)
        user_id = g.user.get("id")

        # Récupérer la liste des documents depuis la base
        rows = fetch_all(
            "SELECT id, object_name, name_document, taille_octets, destination_email, created_at, expires_at, max_views, views_count, is_active, token, SEK AS dek_encrypted, iv, sha256 FROM shared_files WHERE id_owner = %s ORDER BY created_at DESC",
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
            expires_at = row.get("expires_at")
            if expires_at is None:
                expires_at_value = None
            elif hasattr(expires_at, "isoformat"):
                expires_at_value = expires_at.isoformat()
            else:
                expires_at_value = str(expires_at)
            documents.append({
                "id": row["id"],
                "object_name": row["object_name"],
                "file_name": row["name_document"],
                "size": row["taille_octets"],
                "last_modified": last_modified,
                "dek_encrypted": row["dek_encrypted"],
                "iv": row["iv"],
                "sha256": row["sha256"],
                "destination_email": row["destination_email"],
                "expires_at": expires_at_value,
                "is_active": row["is_active"],
                "max_views": row["max_views"],
                "views_count": row["views_count"],
                "token": row["token"]
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


@share.route("/share/switch", methods=["POST"])
def disable_shared_document():
    """
    Swiitch le statue d'un document partagé (0/1)

    Payload attendu:
    {
        "id": "id_du_partage",
    }
    """
    try:
        user_id = g.user.get("id")
        data = request.get_json()
        id = data.get("id")

        # Récupérer la liste des documents depuis la base
        rows = fetch_all(
            "SELECT is_active FROM shared_files WHERE id = %s AND id_owner = %s",
            (id, user_id),
        )
        if len(rows) == 0:
            return api_response({"status": "error", "message": "Partage non trouvé"}, 404, user_id, "Share not found")
        
        current_status = rows[0]["is_active"]
        new_status = 0 if current_status == 1 else 1

        rowcount, t = execute_write(
            "UPDATE shared_files SET is_active = %s WHERE id = %s",
            (new_status, id),
        )

        return api_response({
            "status": "success",
            "message": "Statut mis à jour"
        }, 200, user_id, "Share status updated")    
    
    except Exception as e:
        print(f"[ERROR] Switch shared document: {e}")
        return api_response({"status": "error", "message": f"Erreur lors de la mise à jour: {str(e)}"}, 500, user_id, f"Switch error: {str(e)}")
    

@share.route("/share/name_file", methods=["POST"])
def name_file():
    """
    donne le nom du fichier a partire du token

    Payload attendu:
    {
        "token": "token_du_partage",
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        token = data.get("token")
        if not token:
            return api_response({"status": "error", "message": "Token manquant"}, 400, None, "Share token missing")
        name = fetch_one(
            "SELECT name_document FROM shared_files WHERE token = %s",
            (token,),
        )
        if name is None:
            return api_response({"status": "error", "message": "Partage non trouvé"}, 404, None, "Share not found") 
        return api_response({
            "status": "success",
            "file_name": name["name_document"]
        }, 200, None, "Share name retrieved")
    except Exception as e:
        print(f"[ERROR] Get shared file name: {e}")
        return api_response({"status": "error", "message": f"Erreur lors de la récupération du nom: {str(e)}"}, 500, None, f"Get name error: {str(e)}")


@share.route("/share/download", methods=["POST"])
def download_shared_document():
    """
    Télécharge un document chiffré partagé

    Payload attendu:
    {
        "token": "token_du_partage",
        "email": "email_de_la_personne"
    }
    """

    try:
        data = request.get_json(silent=True) or {}
        
        token = data.get("token")
        email = data.get("email")
        if not token or not email:
            return api_response({"status": "error", "message": "Paramètres manquants"}, 400, None, "Share download missing parameters")
        
        name = fetch_one(
            "SELECT id, id_owner, name_document, destination_email, views_count, max_views, expires_at, is_active FROM shared_files WHERE token = %s",
            (token,),
        )
        if name is None:
            return api_response({"status": "error", "message": "Partage non trouvé"}, 404, None, "Share not found")
        
        if name["destination_email"] != email:
            return api_response({"status": "error", "message": "Email non autorisé"}, 403, None, "Share download denied: email mismatch")
        
        user_id = name["id_owner"]
        max_uses = name["max_views"]
        uses = name["views_count"]
        expires_at = name["expires_at"]
        is_active = name["is_active"]
        id_shared_file = name["id"]

        if max_uses is not None and uses >= max_uses:
            return api_response({"status": "error", "message": "Nombre maximum de téléchargements atteint"}, 403, None, "Share download denied: max views reached")
        if expires_at is not None and datetime.utcnow() > expires_at:
            return api_response({"status": "error", "message": "Le lien a expiré"}, 403, None, "Share download denied: link expired")
        if is_active == 0:
            return api_response({"status": "error", "message": "Le partage est désactivé"}, 403, None, "Share download denied: share disabled")

        name_document = name["name_document"]

        document = fetch_one(
            "SELECT object_name, SEK AS dek_encrypted, iv, sha256, name_document FROM shared_files WHERE id_owner = %s AND name_document = %s",
            (user_id, name_document),
        )
        if document is None:
            return api_response({"status": "error", "message": "Accès non autorisé"}, 403, user_id, "Download denied: document not found")

        object_name = document.get("object_name")
        owner_bucket = f"{user_id}_shared"
        bucket_id = owner_bucket if object_name and object_name.startswith(f"{owner_bucket}/") else user_id
        # Télécharger le fichier
        file_data, _ = download_file(bucket_id, object_name)

        # Récupérer le nom original
        original_name = document.get("name_document", "document")

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


        #mettre a jour le limte d'accés
        rowcount, t = execute_write(
            "UPDATE shared_files SET views_count = views_count + 1 WHERE token = %s",
            (token,),
        )

        #mettre les user agend et ip du mec dans les logs des accées de partage
        user_agent = request.headers.get("User-Agent")
        ip_address = request.remote_addr
        

        print(f"[INFO] Shared document accessed: id_shared_file={id_shared_file}, ip_address={ip_address}, user_agent={user_agent}")
        rowcount, t = execute_write(
            "INSERT INTO shared_acces_log (id_shared_file, accessed_at, ip_address, user_agent) VALUES (%s, %s, %s, %s)",
            (id_shared_file, datetime.utcnow(), str(ip_address), str(user_agent))
        )


        return response
        

    except Exception as e:
        print(f"[ERROR] Download shared document: {e}")
        return api_response({"status": "error", "message": f"Erreur lors du téléchargement: {str(e)}"}, 500, None, f"Download error: {str(e)}")


@share.route("/share/delete", methods=["POST"])
def delete_shared_document():
    """
    Supprime un document partagé

    Payload attendu:
    {
        "id": "id_du_partage"
    }
    """
    try:
        user_id = g.user.get("id")
        data = request.get_json(silent=True) or {}
        share_id = data.get("id")
        if not share_id:
            return api_response({"status": "error", "message": "Paramètres manquants"}, 400, user_id, "Share delete missing parameters")

        share = fetch_one(
            "SELECT object_name FROM shared_files WHERE id = %s AND id_owner = %s",
            (share_id, user_id),
        )
        if share is None:
            return api_response({"status": "error", "message": "Partage non trouvé"}, 404, user_id, "Share not found")

        object_name = share.get("object_name")
        if object_name:
            try:
                delete_file(f"{user_id}_shared", object_name)
            except Exception as cleanup_exc:
                print(f"[ERROR] Delete shared file from MinIO: {cleanup_exc}")

        execute_write(
            "DELETE FROM shared_files WHERE id = %s AND id_owner = %s",
            (share_id, user_id),
        )

        return api_response({"status": "success", "message": "Partage supprimé"}, 200, user_id, "Share deleted")
    except Exception as e:
        print(f"[ERROR] Delete shared document: {e}")
        return api_response({"status": "error", "message": f"Erreur lors de la suppression: {str(e)}"}, 500, user_id, f"Delete share error: {str(e)}")
