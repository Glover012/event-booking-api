from typing import ClassVar, Any
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from pydantic import SecretStr

from .config import settings


class PasswordHasher:
    _PASSWORD_HASH: ClassVar[PasswordHash] = PasswordHash.recommended() # Argon2 is default

    @classmethod
    def hash_password(cls, password: SecretStr) -> str:
        return cls._PASSWORD_HASH.hash(password.get_secret_value())
    
    @classmethod
    def verify_password(cls, password: str, hashed_password: str) -> bool:
        return cls._PASSWORD_HASH.verify(password, hashed_password)


def create_access_token(
        user_id: int,
        username: str,
        user_role: str,
        ) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id), # PyJWT requires claim to be str
        "username": username,
        "role": user_role,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    return jwt.encode(
        payload=payload,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

def decode_access_token(token: str) -> dict[str, Any]:
    payload = jwt.decode(
        jwt=token,
        key=settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        )
    return payload
