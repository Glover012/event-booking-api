from datetime import datetime, timezone

from ..api.pagination import Page, PaginationParams
from ..schemas.users import ChangePasswordRequest, UserRole, UpdateProfileRequest
from ..schemas.bookings import CreateBookingRequest, BookingResponse, BookingStatus
from ..schemas.events import EventStatus
from ..services.users import UsersService
from ..services.events import EventsService
from ..services.bookings import BookingsService
from ..core.security import PasswordHasher
from ..db.models import Users, Bookings
from ..api.exceptions import HTTPError
from ..schemas.auth import MeTokenClaims


class UserAssistant:
    """
    Root of the assistant hierarchy and the helper for user level routes.

    Every account is a user, so the higher roles inherit from here.

    A higher role reaching a lower role's route is handled by the MINIMUM_ROLE check.

    This class supplies all db services, therfore sub-classes don't need their
    own constructors.
    """

    MINIMUM_ROLE = UserRole.USER

    def __init__(
            self,
            me_token_claims: MeTokenClaims,
            users_service: UsersService,
            events_service: EventsService,
            bookings_service: BookingsService,
            ) -> None:
        self.me_token_claims = me_token_claims
        self.users_service = users_service
        self.events_service = events_service
        self.bookings_service = bookings_service
        self.me_model = self.verify_me()

    def verify_me(self) -> Users:
        """
        Confirms that the token data still matches a record in db and
        that its role reaches MINIMUM_ROLE.

        A missing record means the account was removed while the token
        stayed valid, so it ends as an authentication failure. An
        insufficient role ends as forbidden.
        """
        me_model = self.users_service.find_by_identity(
            id=self.me_token_claims.id,
            username=self.me_token_claims.username,
            email=self.me_token_claims.email,
        )

        if me_model is None:
            raise HTTPError.AUTHENTICATION_FAILED()

        if UserRole(me_model.role).level < self.MINIMUM_ROLE.level:
            raise HTTPError.FORBIDDEN()

        return me_model

    def get_me(self) -> Users:
        return self.me_model

    def change_me_password(
            self,
            change_password_request: ChangePasswordRequest,
            ) -> None:

        if not PasswordHasher.verify_password(
            change_password_request.old_password,
            self.me_model.hashed_password,
            ):
            raise HTTPError.INCORRECT_PASSWORD()

        if PasswordHasher.verify_password(
            change_password_request.new_password,
            self.me_model.hashed_password,
        ):
            raise HTTPError.SAME_PASSWORD()

        self.users_service.update_password(
            self.me_model,
            PasswordHasher.hash_password(
                change_password_request.new_password
            ),
        )

    def update_me_profile(
            self,
            update_profile_request: UpdateProfileRequest,
            ) -> Users:
        """
        Updates the caller's own profile. The account is always self.me_model,
        so no target ever arrives from the request.
        """
        return self.users_service.update_profile(
            self.me_model,
            first_name=update_profile_request.first_name,
            last_name=update_profile_request.last_name,
        )

    def book_event(
            self,
            event_id: int,
            create_booking_request: CreateBookingRequest,
            ) -> Bookings:
        """
        BOOKING PATH
        ---
        Books ticket on a publicly visible event for the caller.

        Sequence:
        1. Event row is locked by get_bookable_model_for_update, therefore
        all subsequence booking attemps will be waiting in queue.
        2. Confirm event status and check time.
        3. Check for overbooking.
        4. Create confirmed booking.
        """
        event_model = self.events_service.get_bookable_model_for_update(event_id)

        if (
            event_model.status != EventStatus.ACTIVE.value
            or event_model.starts_at <= datetime.now(timezone.utc)
        ):
            raise HTTPError.EVENT_NOT_BOOKABLE()

        confirmed_tickets = self.bookings_service.count_confirmed_tickets(event_id)

        if confirmed_tickets + create_booking_request.ticket_amount > event_model.capacity:
            raise HTTPError.NOT_ENOUGH_TICKETS()

        return self.bookings_service.create(
            user_id=self.me_model.id,
            event_id=event_id,
            ticket_amount=create_booking_request.ticket_amount,
        )

    def list_me_bookings(
            self,
            pagination: PaginationParams,
            ) -> Page[BookingResponse]:
        """
        Returns one page of the caller's own bookings, cancelled ones
        included, so the account keeps its full history.

        The page is built here, not in the router, so every listing endpoint
        just wraps the data in ApiResponse.
        """
        models, total = self.bookings_service.list_user_owned_models(
            user_id=self.me_model.id,
            limit=pagination.per_page,
            offset=pagination.offset,
        )

        return Page[BookingResponse].create(
            items=models,
            total=total,
            pagination=pagination,
        )

    def cancel_me_booking(self, booking_id: int) -> Bookings:
        """
        Cancels one of the caller's own bookings.

        Changes only booking status to cancelled, therefore
        the tickets goes back to the pool, beacause only
        confirmed are taken into account while booking.
        """
        booking_model = self.bookings_service.get_user_owned_model(
            user_id=self.me_model.id,
            booking_id=booking_id,
        )

        if booking_model.status == BookingStatus.CANCELLED.value:
            raise HTTPError.BOOKING_ALREADY_CANCELLED()

        return self.bookings_service.cancel(booking_model)
