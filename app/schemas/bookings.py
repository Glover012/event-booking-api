from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field



class BookingStatus(StrEnum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class CreateBookingRequest(BaseModel):
    """
    Ticket reservation form. The event comes from the path, the user
    from the token.
    """

    model_config = ConfigDict(
        extra="forbid"
        )

    ticket_amount: int = Field(gt=0, lt=11)


class BookingResponse(BaseModel):
    """Response model with Booking attributes."""

    # Construct response model from SQLAlchemy model
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    ticket_amount: int
    status: BookingStatus
    created_at: datetime
