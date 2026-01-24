from flask import Blueprint, jsonify, request



document = Blueprint("document", __name__)

#TODO need to connect to minio
@document.post("/upload")
def upload():

    name = request.form.get("name")
    file = request.files["file"]


    return jsonify({"status": "ok"})