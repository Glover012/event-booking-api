from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db.models import Events, Bookings
from ..schemas.events import CreateEventRequest, EventStatus, UpdateEventRequest
from ..schemas.bookings import BookingStatus
from ..api.exceptions import HTTPError


class EventsService:
    """
    Provide ready to use db services for the Events table.
    """

    def __init__(self, db: Session):
        self.db = db

    def public_query(self):
        """
        Base query for everything a client may see without authentication.

        Only `public` is filtered. The ck_events_draft_not_public constraint
        makes a public draft impossible, therefore drafts are excluded by the
        database and any second condition is not required here.
        """
        return self.db.query(Events).filter(Events.public.is_(True))

    def get_public_model(self, event_id: int) -> Events:
        """
        Loads a single publicly visible event, based on event ID.

        A draft and a missing id raise the same 404, so the response never
        reveals that a hidden event exists.
        """
        model = self.public_query().filter(Events.id == event_id).first()

        if model is None:
            raise HTTPError.EVENT_DOES_NOT_EXIST()
        return model

    def list_public_models(
            self,
            limit: int,
            offset: int,
            ) -> tuple[list[Events], int]:
        """
        Returns one page of publicly visible events with the total row count
        required by the Page model and the API client.

        Ordered deterministically: newest first, with id breaking ties.
        Without a deterministic order OFFSET may return the same row on 
        two pages or skip one entirely.
        """
        query = self.public_query()

        # Counted before limit/offset, so it describes every matching row,
        # not just the page
        total = query.count()

        models = (
            query.order_by(Events.starts_at.desc(), Events.id.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        return models, total

    def create(
            self,
            create_event_request: CreateEventRequest,
            owner_id: int,
            ) -> Events:
        """
        Inserts a new event. Owner comes from the authenticated and verified
        organizer and status always starts as draft, so neither is taken from 
        the request body.
        """
        try:
            new_event = Events(
                name=create_event_request.name,
                description=create_event_request.description,
                location=create_event_request.location,
                capacity=create_event_request.capacity,
                starts_at=create_event_request.starts_at,
                ends_at=create_event_request.ends_at,
                status=EventStatus.DRAFT.value,
                owner_id=owner_id,
            )
            self.db.add(new_event)
            self.db.commit()
            # Reloads server_default columns
            self.db.refresh(new_event)

            return new_event

        except IntegrityError as e:
            self.db.rollback()
            raise HTTPError.TRANSACTION_REFUSED() from e

    def get_bookable_model_for_update(self, event_id: int) -> Events:
        """
        BOOKING PATH
        ---
        Loads a publicly visible event and locks its row until the
        transaction ends. All subsequent booking attemps on the
        same event will be added to queue.
        """
        model = (
            self.public_query()
            .filter(Events.id == event_id)
            .with_for_update()
            .first()
        )

        if model is None:
            raise HTTPError.EVENT_DOES_NOT_EXIST()
        return model

    def get_user_owned_model(
            self,
            owner_id: int,
            event_id: int,
            for_update: bool = False,
            ) -> Events:
        """
        Returns the event model only that belongs to the User.

        Raise the same error when event doesn't exists and
        when it belongs to different User.

        `for_update=True` additionaly locks the `Events` row until
        the transaction ends, the same way the booking path does.
        """
        query = self.db.query(Events).filter(
            and_(
                Events.id == event_id,
                Events.owner_id == owner_id
            ),
        )

        if for_update:
            query = query.with_for_update()

        event_model = query.first()

        if event_model is None:
            raise HTTPError.EVENT_DOES_NOT_EXIST()
        return event_model

    def list_user_owned_models(
            self,
            owner_id: int,
            limit: int,
            offset: int,
            ) -> tuple[list[Events], int]:
        """
        Returns one page of the events the account owns with the total row
        count required by the Page model and the API client.

        public_query is not reused here, since the owner has to see all
        its events, including the Drafts. A draft is what gets published later.

        Ordered deterministically: newest first, with id breaking ties.
        Without a deterministic order OFFSET may return the same row on two
        pages or skip one entirely.
        """
        query = self.db.query(Events).filter(Events.owner_id == owner_id)

        # Counted before limit/offset, so it describes every matching row,
        # not just the page
        total = query.count()

        models = (
            query.order_by(Events.starts_at.desc(), Events.id.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        return models, total

    def update_status(
            self,
            event_model: Events,
            status: EventStatus,
            ) -> Events:
        """
        Set a new status on an existing event.

        Legal transitions are determined by the assistant.
        """
        try:
            event_model.status = status.value
            self.db.add(event_model)
            self.db.commit()
            self.db.refresh(event_model)

            return event_model

        except IntegrityError as e:
            self.db.rollback()
            raise HTTPError.TRANSACTION_REFUSED() from e

    def publish(self, event_model: Events) -> Events:
        """
        Marks an event as publicly visible.

        Terminal operation that cannot be undone.
        """
        try:
            event_model.public = True
            self.db.add(event_model)
            self.db.commit()
            self.db.refresh(event_model)

            return event_model

        except IntegrityError as e:
            self.db.rollback()
            raise HTTPError.TRANSACTION_REFUSED() from e

    def update(
            self,
            event_model: Events,
            update_event_request: UpdateEventRequest,
            ) -> Events:
        """
        Update editable columns of an existing event.

        status and public are configurable thorught their designated
        functions.
        """
        try:
            event_model.name = update_event_request.name
            event_model.description = update_event_request.description
            event_model.location = update_event_request.location
            event_model.capacity = update_event_request.capacity
            event_model.starts_at = update_event_request.starts_at
            event_model.ends_at = update_event_request.ends_at

            self.db.add(event_model)
            self.db.commit()
            self.db.refresh(event_model)

            return event_model

        except IntegrityError as e:
            self.db.rollback()
            raise HTTPError.TRANSACTION_REFUSED() from e

    def cancel(self, event_model: Events) -> Events:
        """
        Cancel an event together with every confirmed booking on it.

        This service method updates also `Bookings` table, since canceling
        an event must cancel confirmed bookings and all must be proceeded
        in a single transaction.

        The bookings are updated with a single UPDATE.
        `Bookings` table may contain thousands of records, therfore
        any attempt to read them is not advised. For that reason
        synchronize_session is set to False.
        """
        try:
            self.db.query(Bookings).filter(
                and_(
                    Bookings.event_id == event_model.id,
                    Bookings.status == BookingStatus.CONFIRMED.value,
                ),
            ).update(
                {Bookings.status: BookingStatus.CANCELLED.value},
                synchronize_session=False,
            )
            # synchronize_session=False, because with the default 'auto' the
            # ORM tries 'evaluate'. It rebuilds the WHERE condition as
            # a Python function to synchronize objects already in the session.
            # Since we never read those objects, that synchronization is pointless.
            # Whats more important is that when 'evaluate' raises
            # UnevaluatableError, the ORM goes to 'fetch' and attaches
            # RETURNING on postgres, so the UPDATE hands back the primary key
            # of every modified row only for all of them to be discarded.
            # That happens whenever SQLAlchemy cannot build a Python function
            # from the WHERE condition, e.g. a subquery or a SQL function.

            event_model.status = EventStatus.CANCELLED.value
            self.db.add(event_model)
            self.db.commit()
            self.db.refresh(event_model)

            return event_model

        except IntegrityError as e:
            self.db.rollback()
            raise HTTPError.TRANSACTION_REFUSED() from e

    def delete(self, event_model: Events) -> None:
        """
        Removes an event row. Only for drafts, which cannot be public 
        and therefore cannot be booked, so nothing references it. 
        
        Additionally ON DELETE RESTRICT on bookings.event_id stays as the
        another protection layer.
        """
        try:
            self.db.delete(event_model)
            self.db.commit()

        except IntegrityError as e:
            self.db.rollback()
            raise HTTPError.TRANSACTION_REFUSED() from e

    def get_model(self, event_id: int) -> Events:
        """
        Loads any event by id, whatever its owner, status or visibility.

        The only read function with no filter on query. Everything else narrows
        the result by visibility, by owner, or by both.
        """
        model = self.db.query(Events).filter(Events.id == event_id).first()

        if model is None:
            raise HTTPError.EVENT_DOES_NOT_EXIST()
        return model

    def list_models(
            self,
            limit: int,
            offset: int,
            ) -> tuple[list[Events], int]:
        """
        Returns one page of every event with the total row count required
        by the Page model and the API client.

        Drafts, cancelled and unpublished events are all included - this is
        the only listing that sees the whole table.

        Ordered deterministically: newest first, with id breaking ties.
        Without a deterministic order OFFSET may return the same row on two
        pages or skip one entirely.
        """
        query = self.db.query(Events)

        # Counted before limit/offset, so it describes every matching row,
        # not just the page
        total = query.count()

        models = (
            query.order_by(Events.starts_at.desc(), Events.id.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        return models, total
