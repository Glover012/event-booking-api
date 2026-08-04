from typing import Annotated

from fastapi import Depends

from .auth import get_current_user
from ..services.users import UserService
from ..dependencies.database import db_dependency


def get_user_service(db: db_dependency) -> UserService:
    return UserService(db)

### Dependencies ###
user_dependency = Annotated[dict, Depends(get_current_user)] # User info from token

user_service_dependency = Annotated[UserService, Depends(get_user_service)]



