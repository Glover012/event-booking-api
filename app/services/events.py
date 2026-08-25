from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db.models import Events
from ..schemas.events import CreateEventRequest, EventStatus
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
