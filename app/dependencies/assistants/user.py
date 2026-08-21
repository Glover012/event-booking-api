from typing import Annotated

from fastapi import Depends

from ...assistants.user import UserAssistant
from ..auth import current_user_dependency
from ..services.users import users_service_dependency


def get_user_assistant(
        users_service: users_service_dependency,
        user_token: current_user_dependency,
        ) -> UserAssistant:
    return UserAssistant(users_service, user_token)


### Dependencies ###
user_assistant_dependency = Annotated[
    UserAssistant, Depends(get_user_assistant)
]
