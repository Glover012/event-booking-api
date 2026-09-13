# Changelog

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

[0.1.0]: https://github.com/Glover012/event-booking-api/releases/tag/v0.1.0
