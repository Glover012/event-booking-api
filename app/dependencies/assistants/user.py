from typing import Annotated

from fastapi import Depends

from ...assistants.user import UserAssistant
from ..auth import me_token_claims_dependency
from ..services.users import users_service_dependency


def get_user_assistant(
        me_token_claims: me_token_claims_dependency,
        users_service: users_service_dependency,
        ) -> UserAssistant:
    return UserAssistant(me_token_claims, users_service)


### Dependencies ###
user_assistant_dependency = Annotated[
    UserAssistant, Depends(get_user_assistant)
]
