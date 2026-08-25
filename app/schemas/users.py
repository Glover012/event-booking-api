from enum import StrEnum
import re

from pydantic import BaseModel, Field, SecretStr, EmailStr, ConfigDict, field_validator

### Static Error Info ###
PASSWORD_REQUIREMENTS_ERROR = (
    "Password must contain at least one lowercase letter, one uppercase letter, "
    "one digit and one special character"
)

PASSWORD_WHITESPACE_ERROR = "Password must not contain whitespace"


### Validation && Models ###
def validate_password_strength(password: SecretStr) -> SecretStr:
    value = password.get_secret_value()

    has_whitespace = bool(re.search(r"\s", value))
    has_lowercase = any(char.islower() for char in value)
    has_uppercase = any(char.isupper() for char in value)
    has_digit = any(char.isdigit() for char in value)
    has_special_character = any(not char.isalnum() for char in value)

    if has_whitespace:
        raise ValueError(PASSWORD_WHITESPACE_ERROR)

    if not all([has_lowercase, has_uppercase, has_digit, has_special_character]):
        raise ValueError(PASSWORD_REQUIREMENTS_ERROR)

    return password


class UserRole(StrEnum):
    ADMIN = "admin"
    ORGANIZER = "organizer"
    USER = "user"

    @property
    def level(self) -> int:
        return _ROLE_LEVELS[self]

_ROLE_LEVELS = {
    UserRole.USER: 10,
    UserRole.ORGANIZER: 20,
    UserRole.ADMIN: 30,
}

class UserResponse(BaseModel):
    """Response model with User attributes."""

    # Construct response model from SQLAlchemy model
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    username: str
    role: UserRole
    first_name: str
    last_name: str


class RegisterUserRequest(BaseModel):
    """User register request form. Validates request data and password."""

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
        # due to mode="before", therefore an object type
        if isinstance(value, str):
            return value.strip()
        return value

    # Runs validate_password_strength for "password" field model
    @field_validator("password") 
    @classmethod
    def validate_requested_password(cls, password: SecretStr):
        return validate_password_strength(password)


class ChangePasswordRequest(BaseModel):
    old_password: SecretStr
    new_password: SecretStr = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, new_password: SecretStr):
        return validate_password_strength(new_password)


class ChangeRoleRequest(BaseModel):
    """Role change request, admin only."""

    model_config = ConfigDict(extra="forbid")

    role: UserRole


class UpdateProfileRequest(BaseModel):
    """Profile edit form. Email, username and id stay out of reach."""

    model_config = ConfigDict(
        extra="forbid"
        ) # No additional parameters allowed

    first_name: str = Field(min_length=1, max_length=32)
    last_name: str = Field(min_length=1, max_length=32)

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def strip_text_fields(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value
