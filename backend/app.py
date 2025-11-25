from flask import Flask
from dotenv import load_dotenv

from routes import register_blueprints

# Load environment variables for the app and the blueprints.
load_dotenv()


def create_app():
    app = Flask(__name__)
    register_blueprints(app)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
