from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .users import UserRole


### Validation && Models ###
class Token(BaseModel):
    access_token: str
    token_type: str


class UserTokenInfo(BaseModel):
    """
    Claims carried by an access token, after validation.

    The role is informational only - every assistant re-reads 
    it additionally from db, therefore a promotion or a degradation 
    takes effect without a nececity of a new token.
    """

    model_config = ConfigDict(
        extra="ignore"
        ) 
    # Token iat and exp are validated during payload decode

    # validation_alias points Pydantic at the "sub" key of 
    # the decoded payload. The int annotation does the 
    # conversion since PyJWT requires sub to be a str, while 
    # SQLAlchemy queries need an int
    id: int = Field(validation_alias="sub")
    username: str
    email: EmailStr
    role: UserRole
