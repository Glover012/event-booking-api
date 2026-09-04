"""Add updated_at triggers

Revision ID: add_updated_at_triggers
Revises: __PREVIOUS__

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
# down_revision is filled in by builder rebuild-schema when this file is copied
# into alembic/versions, since the revision it follows is auto-generated
revision: str = "add_updated_at_triggers"
down_revision: Union[str, Sequence[str], None] = "__PREVIOUS__"
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
