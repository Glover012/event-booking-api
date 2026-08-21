from typing import ClassVar, Any
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from pydantic import SecretStr

from .config import settings


class PasswordHasher:
    _PASSWORD_HASH: ClassVar[PasswordHash] = PasswordHash.recommended() # Argon2 is default

    @classmethod
    def is_hash(cls, value: str) -> bool:
        """
        Checks whether the string matches the format of any hasher
        configured in PasswordHash.recommended().
        """
        return any(hash.identify(value) for hash in cls._PASSWORD_HASH.hashers)

    @classmethod
    def hash_password(cls, password: SecretStr) -> HashedPassword:
        return HashedPassword(
            cls._PASSWORD_HASH.hash(password.get_secret_value())
        )

    @classmethod
    def verify_password(
        cls, password: SecretStr, hashed_password: HashedPassword) -> bool:
        return cls._PASSWORD_HASH.verify(
            password.get_secret_value(),
            hashed_password.get_secret_value(),
        )


class HashedPassword(SecretStr):
    """
    Represents a hashed password. The value stays hidden from the outside,
    since the class inherits from SecretStr.

    Raises ValueError for anything the hasher does not recognise as its
    own output, plaintext included.
    """

    def __init__(self, secret_value: str) -> None:
        if not PasswordHasher.is_hash(secret_value):
            raise ValueError("HashedPassword requires a password hash")
        super().__init__(secret_value)


def create_access_token(
        user_id: int | str,
        username: str,
        email: str,
        user_role: str,
        ) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id), # PyJWT requires claims to be str
        "username": username,
        "email": email,
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
        # Protection of JWT structure
        # Token must have 'exp' and 'sub' claims
        options={"require": ["exp", "sub"]},
        )
    return payload
