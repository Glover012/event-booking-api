from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, EmailStr


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


class BookingStatusFilter(StrEnum):
    """Query filter for the participant list. ALL drops the condition."""

    ALL = "all"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class ParticipantResponse(BaseModel):
    """One booking together with the account that made it."""

    # A column select returns rows carrying the labels as attributes,
    # so this model is built straight off the join
    model_config = ConfigDict(from_attributes=True)

    booking_id: int
    ticket_amount: int
    status: BookingStatus
    created_at: datetime
    user_id: int
    username: str
    first_name: str
    last_name: str
    email: EmailStr
