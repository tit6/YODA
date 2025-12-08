from flask import jsonify, request, has_request_context
from .db import update_logs

def api_response(data, status, id_user, log_message):
    client_ip = None
    if has_request_context():
        forwarded_for = request.headers.get("X-Forwarded-For", "")
        client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.remote_addr
    if id_user is not None and log_message is not None:
        update_logs(id_user, status, log_message, client_ip)
    return jsonify(data), status
