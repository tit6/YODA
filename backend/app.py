from flask import Flask, jsonify
import pymysql
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

app = Flask(__name__)

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

def get_db_connection():
    """Créer une connexion à la base de données"""
    return pymysql.connect(**db_config)

@app.route('/coucou')
def hello():
    """return coucou for test"""
    return justify({'message': 'coucou'})

@app.route('/db-test')
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)