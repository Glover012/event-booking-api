from typing import Annotated

from fastapi import Depends

from ...assistants.user import UserAssistant
from ..auth import me_token_claims_dependency
from ..services.users import users_service_dependency
from ..services.events import events_service_dependency
from ..services.bookings import bookings_service_dependency


def get_user_assistant(
        me_token_claims: me_token_claims_dependency,
        users_service: users_service_dependency,
        events_service: events_service_dependency,
        bookings_service: bookings_service_dependency,
        ) -> UserAssistant:
    return UserAssistant(
        me_token_claims, users_service, events_service, bookings_service
    )


### Dependencies ###
user_assistant_dependency = Annotated[
    UserAssistant, Depends(get_user_assistant)
]
