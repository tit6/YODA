
import jwt
from config import SECRET_KEY

def encode_jwt(payload: dict, expires_in: int = 3600) -> str:
    """Encode a JWT token with an expiration time."""
    from datetime import datetime, timezone, timedelta

    exp = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    payload.update({"exp": exp})
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token
