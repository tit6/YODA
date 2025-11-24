from flask import Flask, request, session, jsonify, send_from_directory, Response
import secrets
app = Flask(__name__, static_folder='./frontend/dist', static_url_path='')
app.config['SECRET_KEY'] = secrets.token_hex(4096)


@app.route('/')
def serve_vue_app() -> Response:
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path>', methods=['GET', 'POST'])
def serve_static_or_index(path) -> Response:
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)