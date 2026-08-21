from typing import Annotated

from fastapi import Depends

from ...assistants.auth import AuthAssistant
from ..services.users import users_service_dependency


def get_auth_assistant(
        users_service: users_service_dependency,
        ) -> AuthAssistant:
    return AuthAssistant(users_service)


### Dependencies ###
auth_assistant_dependency = Annotated[
    AuthAssistant, Depends(get_auth_assistant)
]
