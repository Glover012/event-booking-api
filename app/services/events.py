from sqlalchemy.orm import Session

from ..db.models import Events
from ..api.exceptions import HTTPError


class EventService:
    """
    Provide ready to use db services for Events table.
    """

    def __init__(self, db: Session):
        self.db = db

    def find_event(self, name: str) -> bool:
        """
        Checks if an event with provided name exists in db.
        Returns True, if found, else False.
        """
        model = self.db.query(Events).filter(Events.name == name).first()

        return model is not None

    def public_query(self):
        """
        Base query for everything a client may see without authentication.

        Only `public` is filtered. The ck_events_draft_not_public constraint
        makes a public draft impossible, so drafts are excluded by the
        database and a second condition is not required here.
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
            raise HTTPError.EVENT_DOES_NOT_EXIST
        return model

    def list_public_models(
            self,
            limit: int,
            offset: int,
            ) -> tuple[list[Events], int]:
        """
        Returns one page of publicly visible events with the total row count
        required by the Page model and the API client.

        Ordered deterministically: newest first, with id winning duel.
        Without a total order OFFSET may return the same row on two pages
        or skip one entirely.
        """
        query = self.public_query()

        # Counted before limit/offset, so it describes every matching row
        total = query.count()

        models = (
            query.order_by(Events.starts_at.desc(), Events.id.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        return models, total
