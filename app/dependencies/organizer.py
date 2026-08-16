from typing import Annotated

from fastapi import Depends

from ..assistants.organizer import OrganizerAssistant
from ..dependencies.database import db_dependency
from ..dependencies.events import event_service_dependency
from ..dependencies.users import user_dependency, user_service_dependency


def get_organizer_assistant(
        db: db_dependency,
        service: user_service_dependency,
        user: user_dependency,
        event_service: event_service_dependency,
        ) -> OrganizerAssistant:
    return OrganizerAssistant(db, service, user, event_service)


### Dependencies ###
organizer_assistant_dependency = Annotated[
    OrganizerAssistant, Depends(get_organizer_assistant)
]
