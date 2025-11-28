from flask import Flask
from dotenv import load_dotenv
from middleware import auth_middleware
from routes import register_blueprints
from routes.files import init_minio

# Load environment variables for the app and the blueprints.
load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB max
    app.before_request(auth_middleware)
    register_blueprints(app)
    return app


app = create_app()

if __name__ == "__main__":
    init_minio()
    app.run(host="0.0.0.0", port=5000, debug=True)
