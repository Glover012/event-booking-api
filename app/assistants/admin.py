from ..schemas.users import UserRole 
from .base import BaseAssistant


class AdminAssistant(BaseAssistant):

    def __init__(self, db, user_service, user) -> None:
        super().__init__(db, user_service, user, UserRole.ADMIN)
