from typing import Annotated

from fastapi import Depends

from ..assistants.public import PublicAssistant
from ..dependencies.events import events_service_dependency
from ..dependencies.users import users_service_dependency


def get_public_assistant(
        users_service: users_service_dependency,
        events_service: events_service_dependency,
        ) -> PublicAssistant:
    return PublicAssistant(users_service, events_service)


### Dependencies ###
public_assistant_dependency = Annotated[
    PublicAssistant, Depends(get_public_assistant)
]
