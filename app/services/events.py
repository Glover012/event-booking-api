from sqlalchemy.orm import Session

from ..db.models import Events


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
