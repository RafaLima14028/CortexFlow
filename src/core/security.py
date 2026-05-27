from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from fastapi import Header, HTTPException, status

from src.core.settings import get_settings


def extract_user_id_by_token(payload: dict) -> str:
    user_id = payload.get("sub", None)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


def get_token_from_header(authorization: str = Header(...)) -> dict:
    schema, _, token = authorization.partition(" ")

    if schema.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    payload = decode_jwt_token(token)

    if extract_user_id_by_token(payload) is None or payload.get("type", None) is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    return payload


def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, get_settings().JWT_SECRET_TOKEN, algorithms=["HS256"]
        )

        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")


def create_jwt_token(
    user_id: str, is_refresh_token: bool = False, token_type: str = "access"
) -> str:
    payload = {"sub": str(user_id), "type": token_type}

    if is_refresh_token:
        payload["exp"] = datetime.now(UTC) + timedelta(days=7)
    else:
        payload["exp"] = datetime.now(UTC) + timedelta(hours=1)

    token = jwt.encode(payload, get_settings().JWT_SECRET_TOKEN, algorithm="HS256")

    return token


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password=password.encode(), salt=bcrypt.gensalt()).decode()


def verify_hashed_password(password_hashed: str, password: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hashed.encode())
