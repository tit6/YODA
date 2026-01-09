from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/health")
def health():
    return jsonify({"status": "ok", "message": "API is running"})


@health_bp.route("/coucou")
def hello():
    return jsonify({"status": "ok"})
