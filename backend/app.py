from flask import Flask, jsonify, request
import pymysql
import os
from dotenv import load_dotenv
from minio import Minio
from minio.error import S3Error
from datetime import timedelta
import uuid
from typing import cast, BinaryIO

# Charger les variables d'environnement depuis .env
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB max

# Configuration MySQL depuis les variables d'environnement
db_config = {
    'host': os.getenv('DATABASE_HOST'),
    'port': int(os.getenv('DATABASE_PORT') or 3306),
    'user': os.getenv('DATABASE_USER'),
    'password': os.getenv('DATABASE_PASSWORD'),
    'database': os.getenv('DATABASE_NAME'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# Configuration MinIO
minio_client = Minio(
    os.getenv('MINIO_ENDPOINT') or 'localhost:9000',
    access_key=os.getenv('MINIO_ACCESS_KEY') or '',
    secret_key=os.getenv('MINIO_SECRET_KEY') or '',
    secure=False
)

# Nom du bucket pour le coffre-fort
BUCKET_NAME = 'coffre-fort'

def get_db_connection():
    """Créer une connexion à la base de données"""
    return pymysql.connect(**db_config)

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

@app.route('/api/coucou')
def hello():
    """return coucou for test"""
    return jsonify({'message': 'coucou'})

@app.route('/api/db-test')
def db_test():
    """Tester la connexion à la base de données"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
        connection.close()
        return jsonify({
            'status': 'success',
            'message': 'Connexion MySQL réussie',
            'mysql_version': version
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload un fichier vers MinIO"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if not file.filename or file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400
        
        # Générer un nom unique pour le fichier
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        object_name = f"{file_id}{file_extension}"
        
        # Upload vers MinIO
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

@app.route('/api/download/<object_name>', methods=['GET'])
def download_file(object_name):
    """Télécharger un fichier depuis MinIO"""
    try:
        # Générer une URL pré-signée valide 1 heure
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

@app.route('/api/files', methods=['GET'])
def list_files():
    """Lister tous les fichiers du coffre-fort"""
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

@app.route('/api/delete/<object_name>', methods=['DELETE'])
def delete_file(object_name):
    """Supprimer un fichier de MinIO"""
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

if __name__ == '__main__':
    init_minio()
    app.run(host='0.0.0.0', port=5000, debug=True)
