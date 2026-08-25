from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db.models import Bookings
from ..schemas.bookings import BookingStatus
from ..api.exceptions import HTTPError


class BookingsService:
    """
    Provide ready to use db services for the Bookings table.
    """

    def __init__(self, db: Session):
        self.db = db

    def count_confirmed_tickets(self, event_id: int) -> int:
        """
        Returns how many tickets the event has already given away.
        Cancelled rows are skipped.

        Has a corresponding Index ix_bookings_event_confirmed.
        """
        # coalesce if NULL return 0
        # Changing filtering options to ex: != 'cancelled' will 
        # skip index, since filter must replicate index condition
        return self.db.query(
            func.coalesce(func.sum(Bookings.ticket_amount), 0)
        ).filter(and_(
            Bookings.event_id == event_id,
            Bookings.status == BookingStatus.CONFIRMED.value
            ),
        ).scalar()

    def create(
            self,
            user_id: int,
            event_id: int,
            ticket_amount: int,
            ) -> Bookings:
        """
        Creates a confirmed booking.
        """
        try:
            new_booking = Bookings(
                user_id=user_id,
                event_id=event_id,
                ticket_amount=ticket_amount,
                status=BookingStatus.CONFIRMED.value,
            )
            self.db.add(new_booking)
            self.db.commit()
            self.db.refresh(new_booking)

            return new_booking

        except IntegrityError as e:
            self.db.rollback()
            raise HTTPError.BOOKING_ALREADY_EXISTS() from e

    def get_user_owned_model(
            self,
            user_id: int,
            booking_id: int,
            ) -> Bookings:
        """
        Returns the booking model only that belongs to 
        User.

        Raise the same error when booking doesn't exists and 
        when it belongs to different User.
        """

        booking_model = self.db.query(Bookings).filter(
            and_(
                Bookings.id == booking_id,
                Bookings.user_id == user_id
            ),
        ).first()

        if booking_model is None:
            raise HTTPError.BOOKING_DOES_NOT_EXIST()
        return booking_model

    def list_user_owned_models(
            self,
            user_id: int,
            limit: int,
            offset: int,
            ) -> tuple[list[Bookings], int]:
        """
        Returns one page of the User bookings with the total row count
        required by the Page model and the API client.

        Cancelled rows are kept in the history.

        Ordered deterministically: newest first, with id breaking ties.
        Without a deterministic order OFFSET may return the same row on 
        two pages or skip one entirely.
        """
        query = self.db.query(Bookings).filter(Bookings.user_id == user_id)

        # Counted before limit/offset, so it describes every matching row,
        # not just the page
        total = query.count()

        models = (
            query.order_by(Bookings.created_at.desc(), Bookings.id.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        return models, total

    def cancel(self, booking_model: Bookings) -> Bookings:
        """
        Moves a booking out of the confirmed state.

        The row stays in the table and leaves uq_bookings_active index,
        which frees the pair and lets the account book the same event again.
        Its tickets stop counting towards the event capacity, since
        count_confirmed_tickets sums confirmed rows only.
        """
        try:
            booking_model.status = BookingStatus.CANCELLED.value
            self.db.add(booking_model)
            self.db.commit()
            self.db.refresh(booking_model)

            return booking_model

        except IntegrityError as e:
            self.db.rollback()
            raise HTTPError.TRANSACTION_REFUSED() from e
