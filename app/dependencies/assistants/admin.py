from typing import Annotated

from fastapi import Depends

from ...assistants.admin import AdminAssistant
from ..auth import me_token_claims_dependency
from ..services.users import users_service_dependency
from ..services.events import events_service_dependency
from ..services.bookings import bookings_service_dependency


def get_admin_assistant(
        me_token_claims: me_token_claims_dependency,
        users_service: users_service_dependency,
        events_service: events_service_dependency,
        bookings_service: bookings_service_dependency,
        ) -> AdminAssistant:
    return AdminAssistant(
        me_token_claims, users_service, events_service, bookings_service
        )


### Dependencies ###
admin_assistant_dependency = Annotated[
    AdminAssistant, Depends(get_admin_assistant)
]
