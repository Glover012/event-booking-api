from ..schemas.events import CreateEventRequest
from ..schemas.users import UserRole
from ..schemas.auth import UserTokenInfo
from ..services.events import EventsService
from ..services.users import UsersService
from ..db.models import Events
from .user import UserAssistant

class OrganizerAssistant(UserAssistant):
    """Helper for organizer level routes. Adds event ownership operations."""

    MINIMUM_ROLE = UserRole.ORGANIZER

    def __init__(
            self,
            users_service: UsersService,
            user_token: UserTokenInfo,
            events_service: EventsService,
            ) -> None:
        super().__init__(users_service, user_token)
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
            owner_id=self.user_model.id,
        )
