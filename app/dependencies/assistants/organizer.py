from typing import Annotated

from fastapi import Depends

from ...assistants.organizer import OrganizerAssistant
from ..auth import current_user_dependency
from ..services.events import events_service_dependency
from ..services.users import users_service_dependency


def get_organizer_assistant(
        users_service: users_service_dependency,
        user_token: current_user_dependency,
        events_service: events_service_dependency,
        ) -> OrganizerAssistant:
    return OrganizerAssistant(users_service, user_token, events_service)


### Dependencies ###
organizer_assistant_dependency = Annotated[
    OrganizerAssistant, Depends(get_organizer_assistant)
]
