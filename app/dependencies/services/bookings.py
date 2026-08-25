from typing import Annotated

from fastapi import Depends

from ...services.bookings import BookingsService
from ..database import db_dependency


def get_bookings_service(db: db_dependency) -> BookingsService:
    return BookingsService(db)


### Dependencies ###
bookings_service_dependency = Annotated[
    BookingsService, Depends(get_bookings_service)
]
