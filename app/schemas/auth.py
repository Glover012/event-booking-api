from pydantic import BaseModel

### Validation && Models ###
class Token(BaseModel):
    access_token: str
    token_type: str
