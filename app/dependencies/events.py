from typing import Annotated

from fastapi import Depends

from ..services.events import EventService
from ..dependencies.database import db_dependency


def get_event_service(db: db_dependency) -> EventService:
    return EventService(db)


### Dependencies ###
event_service_dependency = Annotated[EventService, Depends(get_event_service)]
