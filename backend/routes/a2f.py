from flask import Blueprint, request, g
from module.jwt_ag import encode_jwt
from module.db import fetch_one, execute_write
import base64
import io
import pyotp
import qrcode
import qrcode.image.pure
from bcrypt import checkpw
from module.api_retour import api_response

active_a2f = Blueprint("a2f", __name__)
check_a2f = Blueprint("a2fc", __name__)
diable_a2f = Blueprint("a2fd", __name__)
login_a2f = Blueprint("login_a2f", __name__)
statue_a2f_route = Blueprint("statue_a2f_route", __name__)


def fetch_user_fields(user_id: int, fields: tuple[str, ...]):
    """Small helper to avoid repeating SELECTs on users."""
    column_list = ", ".join(fields)
    return fetch_one(f"SELECT {column_list} FROM users WHERE id = %s", (user_id,))


def is_password_valid(password: str, hashed_password: str) -> bool:
    return checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


@diable_a2f.route("/disable_a2f", methods=["POST"])
def a2fd():
    id_user = g.user["id"]
    password = request.json.get("password")
    if password is None:
        return api_response({"status": "error"}, 400, id_user, "2FA disable failed: missing password")
    
    mdp = fetch_user_fields(id_user, ("mdp",))
    if mdp is None:
        return api_response({"status": "error"}, 404, id_user, "2FA disable failed: user not found")
    if not is_password_valid(password, mdp["mdp"]):
        return api_response({"status": "error"}, 401, id_user, "2FA disable failed: bad password")

    if not update_otp_status("Null", 0, id_user):
        return api_response({"status": "error"}, 500, id_user, "2FA disable failed: DB error")

    return api_response({"status": "success"}, 200, id_user, "Disabled 2FA")
    


@check_a2f.route("/check_a2f", methods=["POST"])
def a2fc():
    id_user = g.user["id"]

    code = request.json.get("otp")
    if code is None:
        return api_response({"status": "error"}, 400, id_user, "2FA check failed: missing OTP")

    mdp = fetch_user_fields(id_user, ("email", "mdp", "secret_a2f"))
    if mdp is None:
        return api_response({"status": "error"}, 404, id_user, "2FA check failed: user not found")
    if mdp["secret_a2f"] == "Null":
        return api_response({"status": "error"}, 400, id_user, "2FA check failed: not activated")
    
    secret = mdp["secret_a2f"]

    totp = pyotp.TOTP(secret)

    # Verify the code
    if totp.verify(code):
        update_otp_status(secret, 2, id_user)
        return api_response({'status': "success"}, 200, id_user, "Successful 2FA verification")
    else:
        update_otp_status(secret, 0, id_user)
        return api_response({'status': "error"}, 401, id_user, "2FA check failed: invalid OTP")


@login_a2f.route("/a2f_login", methods=["POST"])
def validate_a2f():
    """Validate OTP without changing activation status."""
    id_user = g.user["id"]
    a2f_statue = g.user["a2f"]
    if a2f_statue != 1:
        return api_response({"status": "error"}, 400, id_user, "2FA validate failed: not required")

    code = request.json.get("otp")
    if code is None:
        return api_response({"status": "error"}, 401, id_user, "2FA validate failed: missing OTP")

    user = fetch_user_fields(id_user, ("secret_a2f", "statue_a2f"))
    if user is None:
        return api_response({"status": "error"}, 402, id_user, "2FA validate failed: user not found")
    if user["secret_a2f"] == "Null" or user.get("statue_a2f") != 2:
        return api_response({"status": "error"}, 403, id_user, "2FA validate failed: not activated")

    totp = pyotp.TOTP(user["secret_a2f"])
    if totp.verify(code):
            token = encode_jwt({"user_id": id_user, "a2f" : 0}, expires_in=3600)
            message = "Login successful with 2FA"
            
            return api_response({"status": "success", "token": token}, 200, id_user, message)

    return api_response({'success': False}, 401, id_user, "2FA validate failed: invalid OTP")



@active_a2f.route("/active_a2f", methods=["POST"])
def a2f():
    id_user = g.user["id"]
    current_status = check_a2f_status(id_user)
    if current_status == 2:
        return api_response({"status": "error"}, 400, id_user, "2FA activation blocked: already active")
    
    password = request.json.get("password")

    if password is None:
        return api_response({"status": "error"}, 400, id_user, "2FA activation failed: missing password")

    mdp = fetch_user_fields(id_user, ("email", "mdp"))
    if mdp is None:
        return api_response({"status": "error"}, 404, id_user, "2FA activation failed: user not found")

    if not is_password_valid(password, mdp["mdp"]):
        return api_response({"status": "error"}, 401, id_user, "2FA activation failed: bad password")

    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    provisioning_url = totp.provisioning_uri(name=str(id_user), issuer_name="YODA")

    qr_code_base64 = generate_qr_code(provisioning_url)
    
    if not update_otp_status(secret, 1, id_user):
        return api_response({"status": "error"}, 500, id_user, "2FA activation failed: DB error")

    return api_response({
        "status": "success",
        "user": id_user,
        "url": provisioning_url,
        "secret": secret,
        "qrcode": f"data:image/png;base64,{qr_code_base64}",
    }, 200, id_user, "Activated 2FA")
    
@statue_a2f_route.route("/statue_a2f", methods=["GET"])
def test_a2f():
    id_user = g.user["id"]
    statue = check_a2f_status(id_user)
    return api_response({"status": statue}, 200, id_user, f"statue A2F check is : {statue}")

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
