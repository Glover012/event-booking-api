from ..api.pagination import Page, PaginationParams
from ..schemas.events import (
    ChangeEventStatusRequest,
    CreateEventRequest,
    EventResponseOwner,
    EventStatus,
    UpdateEventRequest,
)
from ..schemas.bookings import BookingStatusFilter, ParticipantResponse
from ..schemas.users import UserRole
from ..db.models import Events
from .user import UserAssistant
from ..api.exceptions import HTTPError

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

    def change_event_status(
            self,
            event_id: int,
            change_status_request: ChangeEventStatusRequest,
            ) -> Events:
        """
        Change the caller's own event status.

        Change status uses `FOR UPDATE`, the same way like any booking path,
        therefore the `Event` row is locked for the whole transaction. Any booking 
        operation cannot land while changing the current status and writing a 
        new one, since booking possibility is determined by the event status.

        Cancelling is unreachable here, since it has to cancel the bookings in the 
        same transaction.
        """
        event_model = self.events_service.get_user_owned_model(
            owner_id=self.me_model.id,
            event_id=event_id,
            for_update=True,
        )

        current_status = EventStatus(event_model.status)
        new_status = change_status_request.status

        if new_status is current_status:
            raise HTTPError.SAME_STATUS()

        if new_status not in current_status.next_statuses:
            raise HTTPError.INVALID_STATUS_TRANSITION({
                "current": current_status,
                "allowed": sorted(current_status.next_statuses),
            })

        return self.events_service.update_status(event_model, new_status)

    def publish_event(self, event_id: int) -> Events:
        """
        Opens the caller's own event to the public view.

        This is the only place that sets public = true. It decides
        whether an event is reachable through public GET /events.

        Publish can be only be performed once, only on a active event.

        Uses `FOR UPDATE` for the transaction.
        """
        event_model = self.events_service.get_user_owned_model(
            owner_id=self.me_model.id,
            event_id=event_id,
            for_update=True,
        )

        if event_model.public:
            raise HTTPError.EVENT_ALREADY_PUBLISHED()

        if EventStatus(event_model.status) is not EventStatus.ACTIVE:
            raise HTTPError.EVENT_NOT_PUBLISHABLE()

        return self.events_service.publish(event_model)

    def update_event(
            self,
            event_id: int,
            update_event_request: UpdateEventRequest,
            ) -> Events:
        """
        Update the editable columns of the caller's own event.

        `FOR UPDATE` on `Event` row is used, so it is locked before the booked 
        tickets are counted, so count_confirmed_tickets always returns real value.

        Editing finished or cancelled events are refused. Their bookings are 
        kept as history.

        Dates are frozen once someone holds a ticket. Moving them would hand
        the attendee a ticket for a date they never agreed to, and there is
        nothing to notify them with yet.

        Changing status to 'locked' isn't required, but should be an option
        that goes along with event eddition on front-end side, especially 
        while decreasing event capacity.
        """
        event_model = self.events_service.get_user_owned_model(
            owner_id=self.me_model.id,
            event_id=event_id,
            for_update=True,
        )

        if EventStatus(event_model.status) in (
            EventStatus.FINISHED,
            EventStatus.CANCELLED,
        ):
            raise HTTPError.EVENT_NOT_EDITABLE()

        confirmed_tickets = self.bookings_service.count_confirmed_tickets(
            event_id
        )

        if update_event_request.capacity < confirmed_tickets:
            raise HTTPError.CAPACITY_BELOW_BOOKED_TICKETS()

        if confirmed_tickets and (
            update_event_request.starts_at != event_model.starts_at
            or update_event_request.ends_at != event_model.ends_at
        ):
            raise HTTPError.EVENT_DATES_LOCKED_BY_BOOKINGS()

        return self.events_service.update(event_model, update_event_request)

    def cancel_event(self, event_id: int) -> Events:
        """
        Cancel the caller's own event and every confirmed booking on it.

        The row is locked first. Then goes cancal transaction.

        A finished event is refused to be canceld, same with draft.
        Draft can be removed with separate endpoint.
        """
        event_model = self.events_service.get_user_owned_model(
            owner_id=self.me_model.id,
            event_id=event_id,
            for_update=True,
        )

        current_status = EventStatus(event_model.status)

        if current_status is EventStatus.CANCELLED:
            raise HTTPError.EVENT_ALREADY_CANCELLED()

        if current_status is EventStatus.FINISHED:
            raise HTTPError.EVENT_NOT_CANCELLABLE()

        if current_status is EventStatus.DRAFT:
            raise HTTPError.EVENT_NOT_CANCELLABLE()

        return self.events_service.cancel(event_model)

    def delete_event(self, event_id: int) -> None:
        """
        Deletes the caller's own draft.

        A draft is the only event that cannot exist publicly and once event
        becomes a public, it can't go back to draft state.
        Draft is never visible, never booked, no history worth keeping. 
        Everything past that point is withdrawn by cancelling.
        """
        event_model = self.events_service.get_user_owned_model(
            owner_id=self.me_model.id,
            event_id=event_id,
            for_update=True,
        )

        if EventStatus(event_model.status) is not EventStatus.DRAFT:
            raise HTTPError.EVENT_NOT_DELETABLE()

        self.events_service.delete(event_model)
