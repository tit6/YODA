from flask import jsonify
from db import update_logs

def api_response(data, status, id_user=None, log_message=None):
    if id_user is not None and log_message is not None:
        update_logs(id_user, status, log_message)
    return jsonify(data), status