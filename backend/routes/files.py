from flask import Blueprint, jsonify, request
from config import minio_client, BUCKET_NAME
from minio.error import S3Error
from datetime import timedelta
import uuid
import os
from typing import cast, BinaryIO

files_bp = Blueprint('files', __name__)

def init_minio():
    """Initialiser MinIO et créer le bucket si nécessaire"""
    try:
        if not minio_client.bucket_exists(BUCKET_NAME):
            minio_client.make_bucket(BUCKET_NAME)
            print(f"Bucket '{BUCKET_NAME}' créé avec succès")
        else:
            print(f"Bucket '{BUCKET_NAME}' existe déjà")
    except S3Error as e:
        print(f"Erreur lors de l'initialisation MinIO: {e}")

@files_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload un fichier vers MinIO avec un UUID unique"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if not file.filename or file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400
        
        # Générer un nom unique : UUID + extension originale
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        object_name = f"{file_id}{file_extension}"
        
        # Calculer la taille du fichier
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        minio_client.put_object(
            BUCKET_NAME,
            object_name,
            cast(BinaryIO, file.stream),
            file_size,
            content_type=file.content_type or 'application/octet-stream'
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Fichier uploadé avec succès',
            'file_id': file_id,
            'object_name': object_name,
            'original_filename': file.filename,
            'size': file_size
        }), 201
    
    except S3Error as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur MinIO: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@files_bp.route('/download/<object_name>', methods=['GET'])
def download_file(object_name):
    """Générer une URL de téléchargement temporaire (valide 1h)"""
    try:
        # URL pré-signée avec expiration
        url = minio_client.presigned_get_object(
            BUCKET_NAME,
            object_name,
            expires=timedelta(hours=1)
        )
        
        return jsonify({
            'status': 'success',
            'download_url': url
        })
    
    except S3Error as e:
        return jsonify({
            'status': 'error',
            'message': f'Fichier non trouvé: {str(e)}'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@files_bp.route('/files', methods=['GET'])
def list_files():
    """Lister tous les fichiers avec leurs métadonnées"""
    try:
        objects = minio_client.list_objects(BUCKET_NAME)
        files = []
        
        for obj in objects:
            files.append({
                'object_name': obj.object_name,
                'size': obj.size,
                'last_modified': obj.last_modified.isoformat() if obj.last_modified else None,
                'etag': obj.etag
            })
        
        return jsonify({
            'status': 'success',
            'files': files,
            'count': len(files)
        })
    
    except S3Error as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@files_bp.route('/delete/<object_name>', methods=['DELETE'])
def delete_file(object_name):
    """Supprimer un fichier du coffre-fort"""
    try:
        minio_client.remove_object(BUCKET_NAME, object_name)
        
        return jsonify({
            'status': 'success',
            'message': 'Fichier supprimé avec succès'
        })
    
    except S3Error as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
