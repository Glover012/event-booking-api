from ..schemas.events import CreateEventRequest
from ..schemas.users import UserRole
from ..schemas.auth import MeTokenClaims
from ..services.events import EventsService
from ..services.users import UsersService
from ..db.models import Events
from .user import UserAssistant

class OrganizerAssistant(UserAssistant):
    """Helper for organizer level routes. Adds event ownership operations."""

    MINIMUM_ROLE = UserRole.ORGANIZER

    def __init__(
            self,
            me_token_claims: MeTokenClaims,
            users_service: UsersService,
            events_service: EventsService,
            ) -> None:
        super().__init__(me_token_claims, users_service)
        self.events_service = events_service

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
