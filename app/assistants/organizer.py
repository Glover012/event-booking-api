from ..api.pagination import Page, PaginationParams
from ..schemas.events import CreateEventRequest, EventResponseOwner
from ..schemas.bookings import BookingStatusFilter, ParticipantResponse
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

    def list_me_events(
            self,
            pagination: PaginationParams,
            ) -> Page[EventResponseOwner]:
        """
        Returns one page of the caller's own events, drafts included.

        The page is built here, not in the router, so every listing endpoint
        just wraps the data in ApiResponse.
        """
        models, total = self.events_service.list_user_owned_models(
            owner_id=self.me_model.id,
            limit=pagination.per_page,
            offset=pagination.offset,
        )

        return Page[EventResponseOwner].create(
            items=models,
            total=total,
            pagination=pagination,
        )

    def list_event_participants(
            self,
            event_id: int,
            booking_status: BookingStatusFilter,
            pagination: PaginationParams,
            ) -> Page[ParticipantResponse]:
        """
        Returns one page of the detailed bookings info made on the caller's 
        own event, each one carrying the User account details.

        At first ownership is checked, so any attemt on reading foreign
        event and a missing one end as 404 error before any booking info is 
        read.
        """
        # Ownership check, only used as a guard function
        self.events_service.get_user_owned_model(
            owner_id=self.me_model.id,
            event_id=event_id,
        )

        models, total = self.bookings_service.list_event_bookings_detailed_models(
            event_id=event_id,
            booking_status=booking_status,
            limit=pagination.per_page,
            offset=pagination.offset,
        )

        return Page[ParticipantResponse].create(
            items=models,
            total=total,
            pagination=pagination,
        )
