from ..schemas.events import CreateEventRequest
from ..schemas.users import UserRole
from ..db.models import Events
from .user import UserAssistant

class OrganizerAssistant(UserAssistant):
    """Helper for organizer level routes. Adds event ownership operations."""

    MINIMUM_ROLE = UserRole.ORGANIZER

    def create_event(
            self,
            create_event_request: CreateEventRequest,
            ) -> Events:
        """
        Creates an event owned by the authenticated organizer. Owner and
        status never come from the request body.
        """
        return self.events_service.create(
            create_event_request,
            owner_id=self.me_model.id,
        )
