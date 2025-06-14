from jwt import decode, ExpiredSignatureError, InvalidSignatureError
from app import jwt_secret_key
from typing import Any

def check_jwt(jwt_token: str | None):
    decoded_jwt: dict[str, Any] = {}

    if not jwt_token:
        return "none"

    try:
        decoded_jwt = decode(jwt_token, jwt_secret_key, algorithms=["HS256"])
        return decoded_jwt
    except ExpiredSignatureError:
        return "expired"
    except InvalidSignatureError:
        return "invalid"
