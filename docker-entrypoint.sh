#!/bin/sh
set -e

alembic upgrade head
python -m app.cli create-bootstrap-admin

exec "$@"
