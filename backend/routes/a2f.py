from flask import Blueprint, jsonify, request, g

from db import fetch_one, execute_write
import pyotp
from bcrypt import checkpw
import qrcode
import qrcode.image.pure
import base64
import io

active_a2f = Blueprint("a2f", __name__)
check_a2f = Blueprint("a2fc", __name__)
diable_a2f = Blueprint("a2fd", __name__)

@diable_a2f.route("/disable_a2f", methods=["POST"])
def a2fd():
    id_user = g.user["id"]
    password = request.json.get("password")
    if password is None:
        return jsonify({"status": "error", "message": "Missing password"}), 400
    
    mdp = fetch_one("SELECT mdp FROM users WHERE id = %s", (id_user,))
    if mdp is None:
        return jsonify({"status": "error", "message": "the id is not find"}), 404
    
    motdepasse_bytes = password.encode("utf-8")
    hash_bytes = mdp["mdp"].encode("utf-8")
    if not checkpw(motdepasse_bytes, hash_bytes):
        return jsonify({"status": "error", "message": "Invalid password"}), 401

    if not update_otp_status("Null", 0, id_user):
        return jsonify({"status": "error", "message": "Failed to disable 2FA"}), 500
    
    return jsonify({"status": "success", "message": "2FA disabled successfully"}), 200
    


@check_a2f.route("/check_a2f", methods=["POST"])
def a2fc():

    code = request.json.get("otp")
    if code is None:
        return jsonify({"status": "error", "message": "Missing OTP code"}), 400

    id_user = g.user["id"]

    mdp = fetch_one("SELECT email, mdp, secret_a2f FROM users WHERE id = %s", (id_user,))
    if mdp is None:
        return jsonify({"status": "error", "message": "the id is not find"}), 404
    if mdp["secret_a2f"] == "Null":
        return jsonify({"status": "error", "message": "2FA not activated"}), 400
    
    secret = mdp["secret_a2f"]

    totp = pyotp.TOTP(secret)

    # Verify the code
    if totp.verify(code):
        update_otp_status(secret, 2, id_user)
        return jsonify({'success': True}), 200
    else:
        update_otp_status(secret, 0, id_user)
        return jsonify({'success': False}), 401



@active_a2f.route("/active_a2f", methods=["POST"])
def a2f():
    id_user = g.user["id"]

    if check_a2f_status(id_user) == 2:
        return jsonify({"status": "error", "message": "2FA already activated"}), 400
    elif check_a2f_status(id_user) == 1:
        return jsonify({"status": "error", "message": "2FA is medium, please check your otp or desactive"}), 400

    password = request.json.get("password")

    if password is None:
        return jsonify({"status": "error", "message": "Missing password"}), 400

    mdp = fetch_one("SELECT email, mdp FROM users WHERE id = %s", (id_user,))
    if mdp is None:
        return jsonify({"status": "error", "message": "the id is not find"}), 404

    motdepasse_bytes = password.encode("utf-8")
    hash_bytes = mdp["mdp"].encode("utf-8")
    if not checkpw(motdepasse_bytes, hash_bytes):
        return jsonify({"status": "error", "message": "Invalid password"}), 401

    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    provisioning_url = totp.provisioning_uri(name=str(id_user), issuer_name="YODA")

    qr_code_base64 = generate_qr_code(provisioning_url)
    
    if not update_otp_status(secret, 1, id_user):
        return jsonify({"status": "error", "message": "Failed to store secret"}), 500

    return jsonify({
        "status": "success",
        "user": id_user,
        "url": provisioning_url,
        "secret": secret,
        "qrcode": f"data:image/png;base64,{qr_code_base64}",
    }), 200


def generate_qr_code(provisioning_url: str) -> str:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(provisioning_url)
    qr.make(fit=True)

    # Use pure-Python PNG generation (pypng) to avoid PIL/Pillow dependency.
    img = qr.make_image(
        fill_color="black",
        back_color="white",
        image_factory=qrcode.image.pure.PyPNGImage,
    )
    buffered = io.BytesIO()
    img.save(buffered)
    return base64.b64encode(buffered.getvalue()).decode("ascii")


def update_otp_status(secret: str, statue_a2f:int, user_id: int) -> bool:
    try:
        execute_write(
            "UPDATE users SET secret_a2f = %s, statue_a2f=%s WHERE id = %s",
            (secret, statue_a2f, user_id)
        )
        return True
    except Exception as exc:
        print(f"Error updating OTP status: {exc}")
        return False

def check_a2f_status(user_id: int) -> int:
    try:
        result = fetch_one(
            "SELECT statue_a2f FROM users WHERE id = %s",
            (user_id,)
        )
        if result:
            return result["statue_a2f"]
        return 0
    except Exception as exc:
        print(f"Error fetching OTP status: {exc}")
        return 0
