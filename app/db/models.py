from datetime import datetime

from ..core.security import HashedPassword
from .types import HashedPasswordType

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Users(Base):
    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'organizer', 'admin')",
            name="ck_users_role",
        ),
    )

    # SQLAlchemy 2.0 Mapped, set nullable=False by default, unless Mapped[Type | None]
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    # Check types.py for HashedPasswordType mechanics info
    hashed_password: Mapped[HashedPassword] = mapped_column(HashedPasswordType)
    role: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )


class Events(Base):
    __tablename__ = "events"

    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_events_capacity_positive"),
        CheckConstraint(
            "ends_at > starts_at",
            name="ck_events_ends_after_starts",
        ),
        CheckConstraint(
            "status IN ('draft', 'active', 'finished', 'cancelled')",
            name="ck_events_status",
        ),
        CheckConstraint(
            "NOT (status = 'draft' AND public = true)",
            name="ck_events_draft_not_public",
        ),
        Index("ix_events_owner_id", "owner_id"),
        Index("ix_events_starts_at", "starts_at"),
        Index("ix_events_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str] = mapped_column(String)
    capacity: Mapped[int] = mapped_column(Integer)
    public: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("false"),
    )
    status: Mapped[str] = mapped_column(
        String,
        server_default=text("'draft'"),
    )
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        )
    starts_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )


class Bookings(Base):
    __tablename__ = "bookings"

    __table_args__ = (
        CheckConstraint(
            "status IN ('confirmed', 'cancelled')",
            name="ck_bookings_status",
        ),
        CheckConstraint(
            "ticket_amount > 0",
            name="ck_bookings_ticket_amount_positive",
        ),
        # Single pair of user_id and event_id with status = 'confirmed' is allowed
        # in the Index. Otherwise db raises "UniqueViolation" -> SQLAlchemy
        # "IntegrityError".
        # Besides its base Index functionality, it additionally protects the table
        # from multiple reservations of the same user, on the same event.
        # When a user cancels, the status changes to 'cancelled', the row stops
        # matching the Index condition and are dropped out of the Index. 
        # The pair is free again, so the user may re-book - only 'confirmed' 
        # rows are indexed. A UNIQUE(user_id, event_id) would block re-booking completely.
        Index(
            "uq_bookings_active",
            "user_id",
            "event_id",
            unique=True,
            postgresql_where=text("status = 'confirmed'"),
        ),
        Index("ix_bookings_user_id", "user_id"),
        Index("ix_bookings_event_id", "event_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="RESTRICT"),
    )
    status: Mapped[str] = mapped_column(
        String,
        server_default=text("'confirmed'"),
    )
    ticket_amount: Mapped[int] = mapped_column(
        Integer,
        server_default=text("1"),
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )
