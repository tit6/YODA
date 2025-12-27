import os
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv

load_dotenv()

# Configuration MinIO
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = "yoda-documents"

# Client MinIO
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False  # True si HTTPS
)


def init_minio():
    """Initialise le bucket MinIO s'il n'existe pas"""
    try:
        if not minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.make_bucket(MINIO_BUCKET)
            print(f"[MinIO] Bucket '{MINIO_BUCKET}' créé avec succès")
        else:
            print(f"[MinIO] Bucket '{MINIO_BUCKET}' existe déjà")
    except S3Error as e:
        print(f"[MinIO] Erreur lors de l'initialisation: {e}")
        raise


def upload_file(user_id: int, file_data: bytes, file_name: str, metadata: dict) -> str:
    """
    Upload un fichier chiffré dans MinIO

    Args:
        user_id: ID de l'utilisateur
        file_data: Données du fichier chiffré
        file_name: Nom du fichier
        metadata: Métadonnées (dek_encrypted, iv, sha256, etc.)

    Returns:
        object_name: Nom de l'objet dans MinIO
    """
    from io import BytesIO

    # Nom unique pour l'objet: user_id/timestamp_filename
    import time
    timestamp = int(time.time() * 1000)
    object_name = f"{user_id}/{timestamp}_{file_name}"

    try:
        minio_client.put_object(
            MINIO_BUCKET,
            object_name,
            BytesIO(file_data),
            length=len(file_data),
            metadata=metadata,
            content_type="application/octet-stream"
        )
        return object_name
    except S3Error as e:
        print(f"[MinIO] Erreur lors de l'upload: {e}")
        raise


def list_user_files(user_id: int) -> list:
    """
    Liste tous les fichiers d'un utilisateur

    Args:
        user_id: ID de l'utilisateur

    Returns:
        Liste des objets MinIO
    """
    try:
        objects = minio_client.list_objects(
            MINIO_BUCKET,
            prefix=f"{user_id}/",
            recursive=True
        )

        files = []
        for obj in objects:
            # Récupérer les métadonnées
            stat = minio_client.stat_object(MINIO_BUCKET, obj.object_name)

            files.append({
                "object_name": obj.object_name,
                "file_name": obj.object_name.split("/", 1)[1] if "/" in obj.object_name else obj.object_name,
                "size": obj.size,
                "last_modified": obj.last_modified.isoformat(),
                "metadata": stat.metadata
            })

        return files
    except S3Error as e:
        print(f"[MinIO] Erreur lors de la liste: {e}")
        raise


def download_file(user_id: int, object_name: str) -> tuple:
    """
    Télécharge un fichier depuis MinIO

    Args:
        user_id: ID de l'utilisateur
        object_name: Nom de l'objet dans MinIO

    Returns:
        (file_data, metadata)
    """
    try:
        # Vérifier que l'utilisateur a accès au fichier
        if not object_name.startswith(f"{user_id}/"):
            raise PermissionError("Accès non autorisé à ce fichier")

        # Récupérer le fichier
        response = minio_client.get_object(MINIO_BUCKET, object_name)
        file_data = response.read()

        # Récupérer les métadonnées
        stat = minio_client.stat_object(MINIO_BUCKET, object_name)

        return file_data, stat.metadata
    except S3Error as e:
        print(f"[MinIO] Erreur lors du téléchargement: {e}")
        raise
    finally:
        if 'response' in locals():
            response.close()
            response.release_conn()


def delete_file(user_id: int, object_name: str) -> bool:
    """
    Supprime un fichier de MinIO

    Args:
        user_id: ID de l'utilisateur
        object_name: Nom de l'objet dans MinIO

    Returns:
        True si suppression réussie
    """
    try:
        # Vérifier que l'utilisateur a accès au fichier
        if not object_name.startswith(f"{user_id}/"):
            raise PermissionError("Accès non autorisé à ce fichier")

        minio_client.remove_object(MINIO_BUCKET, object_name)
        return True
    except S3Error as e:
        print(f"[MinIO] Erreur lors de la suppression: {e}")
        raise
