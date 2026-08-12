#!/usr/bin/env bash

set -euo pipefail

SECRET_DIR='/var/lib/event-booking/secrets'

SECRETS=(secret_key postgres_password bootstrap_admin_password)

log() { printf '[setup] %s\n' "$*"; }
die() { printf '[setup] ERROR: %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "Run with sudo - $SECRET_DIR belongs to root."

install -d -m 700 "$SECRET_DIR"

umask 077
for name in "${SECRETS[@]}"; do
    path="$SECRET_DIR/$name"
    if [ -s "$path" ]; then
        log "$name already exists - skipping."
    else
        openssl rand -hex 32 > "$path"
        log "$name generated."
    fi
done

log "Building and running stack..."
docker compose up -d --build

log "Ready. Read the bootstrap admin password with:"
log "  sudo cat $SECRET_DIR/bootstrap_admin_password"
