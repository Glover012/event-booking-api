from typing import Annotated
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, Field

from ...core import settings
from ...db import db_dependency


auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

class Token(BaseModel):
    access_token: str
    token_type: str

