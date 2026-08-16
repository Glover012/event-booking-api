from typing import Self
from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, AwareDatetime

from ..api.exceptions import HTTPError


class EventStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class CreateEventRequest(BaseModel):
    """Event creation form. Validates request data and the date range."""

    model_config = ConfigDict(
        extra="forbid"
        ) # No additional parameters allowed

    name: str = Field(min_length=4, max_length=127)
    description: str | None = Field(default=None, max_length=2047)
    location: str = Field(min_length=1, max_length=255)
    capacity: int = Field(gt=0)
    # The event-booking-api operates explicitly on UTC.
    # All timestamp columns are timestamptz, which stores an instant in UTC
    # and does not keep the zone. On read Postgres renders that instant in
    # the session TimeZone, which defaults from the server config - here UTC.
    # A naive datetime (no offset) would be interpreted using that same
    # session setting - so with the session on UTC it is taken as UTC, but
    # on a server configured otherwise it would silently mean something else.
    # AwareDatetime forces the client to send tzinfo, so the instant is
    # unambiguous no matter how the database server happens to be configured.
    starts_at: AwareDatetime
    ends_at: AwareDatetime

    @field_validator("name", "description", "location", mode="before")
    @classmethod
    def strip_text_fields(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    # Two rules here. The start past-date check has no counterpart 
    # in the database, it only guards against obvious client mistakes.
    # The range check mirrors ck_events_ends_after_starts, but raises 422
    # with Pydantic error info instead of a 500 from the database server.
    # Both values are aware, so comparison is safe regardless
    # of the timezone client operates on.
    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.starts_at < datetime.now(timezone.utc):
            raise ValueError("Event start date must not be in the past.")

        if self.ends_at <= self.starts_at:
            raise ValueError("Event end date must be later than start.")

        return self


class EventResponse(BaseModel):
    """Response model with Event attributes."""

    # Construct response model from SQLAlchemy model
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    location: str
    capacity: int
    public: bool
    status: EventStatus
    owner_id: int
    starts_at: datetime
    ends_at: datetime
