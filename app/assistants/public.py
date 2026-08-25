from ..api.pagination import Page, PaginationParams
from ..core.security import PasswordHasher
from ..db.models import Events, Users
from ..schemas.events import EventResponsePublic
from ..schemas.users import RegisterUserRequest, UserRole
from ..services.events import EventsService
from ..services.users import UsersService
from ..api.exceptions import HTTPError


class PublicAssistant:
    """
    Helper for public routes reachable without an authenitcation token.

    Outside of the role based UserAssistant hierarchy.
    """

    def __init__(
            self, 
            users_service: UsersService,
            events_service: EventsService,
            ) -> None:
        self.users_service = users_service
        self.events_service = events_service

    ### Users ###
    def register_user(
            self,
            register_user_request: RegisterUserRequest,
            ) -> Users:
        """
        Creates a standard account. The User role is hardcoded, so it can never
        arrive from the request body.

        The credential availability check is addition. The unique db constraints 
        on username and email are what finally decides.
        """
        if self.users_service.credentials_taken(
            username=register_user_request.username,
            email=register_user_request.email,
        ):
            raise HTTPError.USER_ALREADY_EXISTS()

        # Hashing runs only once the account is known to be creatable,
        # since Argon2 is deliberately expensive
        hashed_password = PasswordHasher.hash_password(
            register_user_request.password
        )

        return self.users_service.create(
            email=register_user_request.email,
            username=register_user_request.username,
            first_name=register_user_request.first_name,
            last_name=register_user_request.last_name,
            hashed_password=hashed_password,
            role=UserRole.USER.value,
        )

    ### Events ###
    def get_event(self, event_id: int) -> Events:
        return self.events_service.get_public_model(event_id)

    def list_events(
            self,
            pagination: PaginationParams,
            ) -> Page[EventResponsePublic]:
        """
        Returns one page of publicly visible events.
        
        The page is built here, not in the router, so every listing endpoint
        just wraps the data in ApiResponse.
        """
        models, total = self.events_service.list_public_models(
            limit=pagination.per_page,
            offset=pagination.offset,
        )

        return Page[EventResponsePublic].create(
            items=models,
            total=total,
            pagination=pagination,
        )
