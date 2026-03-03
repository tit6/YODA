from flask import jsonify, request, has_request_context
from .db import update_logs

def api_response(data, status, id_user, log_message):
    client_ip = None
    if has_request_context():
        forwarded_for = request.headers.get("X-Forwarded-For", "")
        client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.remote_addr
    if id_user is not None and log_message is not None:
        # Le logging doit rester best-effort: ne jamais casser la réponse API si l'insert logs échoue
        # (ex: token invalide, user supprimé, contrainte FK, etc.).
        try:
            user_id_int = int(id_user)
        except (TypeError, ValueError):
            user_id_int = None

        if user_id_int is not None:
            try:
                update_logs(user_id_int, status, log_message[:150], client_ip)
            except Exception as exc:
                print(f"[WARNING] update_logs failed for user_id={user_id_int}: {exc}")
    return jsonify(data), status
