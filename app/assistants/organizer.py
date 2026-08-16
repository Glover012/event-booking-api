from sqlalchemy.exc import IntegrityError

from ..schemas.users import UserRole
from ..schemas.events import CreateEventRequest, EventStatus
from ..services.events import EventService
from ..db.models import Events
from ..api.exceptions import HTTPError
from .base import BaseAssistant


class OrganizerAssistant(BaseAssistant):

    def __init__(self, db, user_service, user, event_service: EventService) -> None:
        super().__init__(db, user_service, user, UserRole.ORGANIZER)
        self.event_service = event_service

    def create_event(
            self,
            create_event_request: CreateEventRequest,
            ) -> Events:
        """
        Creates a new event owned by the authenticated organizer.
        Owner and status never come from the request body.
        """

        try:
            new_event = Events(
                name=create_event_request.name,
                description=create_event_request.description,
                location=create_event_request.location,
                capacity=create_event_request.capacity,
                starts_at=create_event_request.starts_at,
                ends_at=create_event_request.ends_at,
                status=EventStatus.DRAFT.value,
                owner_id=self.user_model.id,
            )
            self.db.add(new_event)
            self.db.commit()
            # Reloads model from db
            self.db.refresh(new_event)

            return new_event

        except IntegrityError:
            self.db.rollback()
            raise HTTPError.TRANSACTION_REFUSED
