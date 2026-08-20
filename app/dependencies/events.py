from typing import Annotated

from fastapi import Depends

from ..services.events import EventsService
from ..dependencies.database import db_dependency


def get_events_service(db: db_dependency) -> EventsService:
    return EventsService(db)


### Dependencies ###
events_service_dependency = Annotated[EventsService, Depends(get_events_service)]
