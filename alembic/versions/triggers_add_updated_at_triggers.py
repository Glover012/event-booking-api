"""add updated_at triggers

Revision ID: triggers
Revises: 749b5a1fb63f
Create Date: 2026-08-27 15:53:55.910703

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'triggers'
down_revision: Union[str, Sequence[str], None] = '749b5a1fb63f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS trigger AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """)

    op.execute("""
        CREATE TRIGGER set_users_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION set_updated_at();
        """)

    op.execute("""
        CREATE TRIGGER set_events_updated_at
        BEFORE UPDATE ON events
        FOR EACH ROW
        EXECUTE FUNCTION set_updated_at();
        """)

    op.execute("""
        CREATE TRIGGER set_bookings_updated_at
        BEFORE UPDATE ON bookings
        FOR EACH ROW
        EXECUTE FUNCTION set_updated_at();
        """)

def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS set_bookings_updated_at ON bookings;")
    op.execute("DROP TRIGGER IF EXISTS set_events_updated_at ON events;")
    op.execute("DROP TRIGGER IF EXISTS set_users_updated_at ON users;")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at();")
