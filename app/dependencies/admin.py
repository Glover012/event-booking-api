from typing import Annotated

from fastapi import Depends

from ..assistants.admin import AdminAssistant
from ..dependencies.events import events_service_dependency
from ..dependencies.users import current_user_dependency, users_service_dependency


def get_admin_assistant(
        users_service: users_service_dependency,
        user_token: current_user_dependency,
        events_service: events_service_dependency,
        ) -> AdminAssistant:
    return AdminAssistant(users_service, user_token, events_service)


### Dependencies ###
admin_assistant_dependency = Annotated[
    AdminAssistant, Depends(get_admin_assistant)
]
