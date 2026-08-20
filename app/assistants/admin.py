from ..schemas.users import UserRole
from ..schemas.auth import UserTokenInfo
from ..services.events import EventsService
from ..services.users import UsersService
from .organizer import OrganizerAssistant


class AdminAssistant(OrganizerAssistant):
    """
    Helper for admin level routes.
    """

    MINIMUM_ROLE = UserRole.ADMIN

    def __init__(
            self,
            users_service: UsersService,
            user_token: UserTokenInfo,
            events_service: EventsService,
            ) -> None:
        super().__init__(users_service, user_token, events_service)
