from typing import Annotated

from fastapi import Depends

from ..assistants.admin import AdminAssistant
from ..dependencies.database import db_dependency
from ..dependencies.users import user_dependency, user_service_dependency


def get_admin_assistant(
        db: db_dependency,
        service: user_service_dependency,
        user: user_dependency,
        ) -> AdminAssistant:
    return AdminAssistant(db, service, user)


### Dependencies ###
admin_assistant_dependency = Annotated[
    AdminAssistant, Depends(get_admin_assistant)
]