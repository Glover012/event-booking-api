from typing import Annotated, ClassVar
from enum import StrEnum
import re

from fastapi import APIRouter, status, HTTPException
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field, SecretStr, EmailStr, ConfigDict, field_validator
from pwdlib import PasswordHash

from ...db import Users, db_dependency


### Validation && Models ###
class UserRole(StrEnum):
    ADMIN = "admin"
    ORGANIZER = "organizer"
    USER = "user"


class PasswordHasher:
    _PASSWORD_HASH: ClassVar[PasswordHash] = PasswordHash.recommended() # Argon2 is default

    @classmethod
    def hash_password(cls, password: SecretStr) -> str:
        return cls._PASSWORD_HASH.hash(password.get_secret_value())

class RegisterUserResponse(BaseModel):
    """Response returned after successful user registration."""

    # Construct response model from SQLAlchemy model
    model_config = ConfigDict(from_attributes=True) 

    email: EmailStr
    username: str
    role: UserRole
    first_name: str
    last_name: str

class RegisterUserRequest(BaseModel):
    """User register request form. Validates request data and password."""

    PASSWORD_REQUIREMENTS_ERROR: ClassVar[str] = (
        "Password must contain at least one lowercase letter, one uppercase letter, "
        "one digit and one special character"
        )

    model_config = ConfigDict(
        extra="forbid"
        ) # No additional parameters allowed

    email: EmailStr # Pydantic uses email-validator
    username: str = Field(min_length=4, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    first_name: str = Field(min_length=1, max_length=32)
    last_name: str = Field(min_length=1, max_length=32)
    password: SecretStr = Field(min_length=8, max_length=128)

    # mode="before" = Before Field validation
    @field_validator("email", "username", "first_name", "last_name", mode="before") 
    @classmethod
    def strip_text_fields(cls, value: object) -> object:
        # Technically value may be different from an str, 
        # due to mode="before", therefore object
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("password") # Runs validate_password_strength for password field model
    @classmethod
    def validate_password(cls, password: SecretStr) -> SecretStr:
        value = password.get_secret_value()

        has_whitespace = bool(re.search(r"\s", value))
        has_lowercase = any(char.islower() for char in value)
        has_uppercase = any(char.isupper() for char in value)
        has_digit = any(char.isdigit() for char in value)
        has_special_character = any(not char.isalnum() for char in value)

        if has_whitespace:
            raise ValueError("Password must not contain whitespace")

        if not all([has_lowercase, has_uppercase, has_digit, has_special_character]):
            raise ValueError(cls.PASSWORD_REQUIREMENTS_ERROR)

        return password

### API Router && Dependency ###
user_router = APIRouter(
    prefix="/user",
    tags=["user"]
)


### Endpoints ###
@user_router.post('/', status_code=status.HTTP_201_CREATED, response_model=RegisterUserResponse)
def register_user(
    db: db_dependency, 
    register_user_request: RegisterUserRequest
    ) -> RegisterUserResponse:

    new_user = Users(
        email = register_user_request.email,
        username = register_user_request.username,
        first_name = register_user_request.first_name,
        last_name = register_user_request.last_name,
        role = UserRole.USER.value
        )
    
    user_exists = db.query(Users).filter(
        or_(
            Users.username == register_user_request.username,
            Users.email == register_user_request.email,
            )
            ).first()

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
            )
    
    # Race condition
    try:
        # Due to resource consumption password hashing is proceeded directly
        # before the add/commit, when all user creation conditions are met
        new_user.hashed_password = PasswordHasher.hash_password(
            register_user_request.password
            )
        db.add(new_user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )
    
    return new_user
