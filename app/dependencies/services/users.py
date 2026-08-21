from typing import Annotated

from fastapi import Depends

from ...services.users import UsersService
from ..database import db_dependency


def get_users_service(db: db_dependency) -> UsersService:
    return UsersService(db)


### Dependencies ###
users_service_dependency = Annotated[UsersService, Depends(get_users_service)]
