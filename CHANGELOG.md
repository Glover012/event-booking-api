# Changelog

## [Unreleased]

### Added
- Two Postman collections run by the Postman CLI against a container stack: one chain over all 25 endpoints, and 23 checks asserting the refusals for `401`, `422`, `403`, `404` and `409`
- Dataset selection for `up --seed`, so a run loads either the single admin account or the complete dataset
- Two CI jobs that start the stack and run each test collection

### Fixed
- `builder <env> up --seed <dataset>`, which failed on the GitHub runner because the builder passed `--no-tty` to `compose exec` - a long form that older docker compose versions do not recognise. It now passes `-T`.

## [0.1.0] - 2026-09-13
First release. The complete loop works end to end: register, log in, create an event, publish it, book a ticket, cancel the booking, cancel the event.

### Added
- REST API on FastAPI, 25 endpoints, Swagger UI and a uniform response envelope on every answer, with two documented exceptions
- JWT authentication, Argon2 password hashing, access control by user role and by resource ownership
- The first admin account created on boot when the database holds none
- Request and response validation with Pydantic, and pagination returning the total row count alongside the page count
- Event lifecycle enforced by an allowed-transition map, row locking that prevents overselling, and one active booking per user and event
- PostgreSQL schema with constraints, indexes and triggers, and Alembic migrations applied on container start
- Builder CLI covering both environments, file based secrets, and an optional demo dataset on `up --seed`
- Rotating logs per component, and continuous integration running the unit tests, ruff and mypy

[Unreleased]: https://github.com/Glover012/event-booking-api/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Glover012/event-booking-api/releases/tag/v0.1.0
