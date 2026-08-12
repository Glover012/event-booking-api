#!/usr/bin/env bash

set -euo pipefail

# --wait due to healthcheck, because this compose don't have depends on
docker compose -f docker-compose.local.yaml up -d --wait

alembic upgrade head

python -m app.cli create-bootstrap-admin

uvicorn app.main:create_app --factory --reload
