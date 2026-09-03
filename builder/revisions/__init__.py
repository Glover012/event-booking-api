from pathlib import Path

REVISIONS_DIR = Path(__file__).resolve().parent

# Revisions are applied in this exact order, each one chained to the one before it.
# The first one in the tuple is chained after inital revision, therefore it has 
# initial revision ID in down_revions.
REVISIONS = (
    "add_updated_at_triggers.py",
    )
