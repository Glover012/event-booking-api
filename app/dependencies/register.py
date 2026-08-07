from typing import Annotated

from fastapi import Depends

from ..dependencies.database import db_dependency
from ..dependencies.users import user_service_dependency
from ..services.register import RegisterService

def get_register_service(
        db: db_dependency,
        service: user_service_dependency,
        ) -> RegisterService:
    return RegisterService(db, service)

### Dependencies ###
register_service_dependency = Annotated[RegisterService, Depends(get_register_service)]
