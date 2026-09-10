# 📐 Design
The detailed application design description.

## Table of contents

## Layers
### API structure
routers -> endpoints -> schemas -> dependencies -> assistants -> services
- **Routers**: Each router contains a set of endpoints grupped by a role, that can access them.
- **Endpoints**: The endpoints use dependencies to load required assistant specified for a particular role that can access endpoint.
- **Schemas**: Request froms, response data validation and SQLAlchemy model filtration. Models that are returned from database are filtered by their designated ResponseModel, so any unnecesarry data won't reach the clinet. Each response have a special ApiResponse wrapper that is used to achieve unified response structure for the API client.
- **Dependencies**: Used to load the tools and features that endpoint requires, like Assistant classes or Pagination feature.
- **Assistants**: Each assistant covers user role functions. It shipps the whole endpoint logic, verify user access and token data.
- **Services**: Functions responsible only for database communication. Used only by assistants, never by inside endpoint, since these tools aren't responsible for access control. Serices commits the data and raise database errors.

### Assistant classes && access control
The API endpoint access controll is role-based and all of that resides within assistant clases. Each endpoint is grupped by a role that can access it and these endpoints, via dependency, imports their designated assistant, which controls the endpoint access and confirms user data extracted JWT with database. Assistant classes also includes services, that allows them communicate with database and perform operations on data.

We have 4 types of assistants:
- **PublicAssistant**: for non-authorized users, only public functions.
- **UserAssistant**: for regiseter users with account related options and booking features.
- **OrganizerAssistant**: for event organizer accounts, covers all event related functions. Includes all *UserAssistant* features.
- **AdminAssistant**:  application maintaining account, admin features. Includes all *UserAssistant*  and *OrganizerAssistant* features.

## Access and ownership control
### Access control
Access to an API route and to a database resource is determined by two independent factors: the caller's role and the ownership of the resource.

An account, once promoted to a higher role, does not lose its previous privileges. Instead it inherits them, therefore its access can only widen.

### Ownership control
At first, the designated assistant class extract user data from JWT and confirm it with the database. This is made deliberatly to in this shape to avoid situation when user role is downgraded, since JWT have 30 minute expiration time(configurable).

Then using verified User ID ownership on database resources is checked by WHERE. Any attempt to

## Roles, user types and priviledges
### Roles
User[10] < Organizer[20] < Admin[30]
Each registered account starts as regular User, with basic functionalty. The account role can be upgraded or downgraded by a Admin account. The role permissions are inherited, therefore higher role have also functionality of a leser roles. Organizer keep all User functionality and Admin has those of User and Orgnizer, plus its own.

### Role promotion policy
Every account starts as a **User**. There is no separate registration for an organizer or admin account, and no endpoint that grants a role to its own caller. An account is promoted to **Organizer** or **Admin** only by an **Admin** account. 
The first admin is the exception: it is created on boot from configured credentials when the database holds no admin at all, which is what makes the first promotion possible.

### User types and their privileges
- **Visitor**: an unauthenticated caller, with no account and no access token. Browses published events and can register an account.
- **User**: a registered account with access to the basic operations. Books tickets for active published events, lists its own bookings and cancels them.
- **Organizer**: an account with access to event-oriented endpoints. Creates events, edits them, moves them through their statuses,
publishes them, cancels them, deletes a draft, and reads the participant list of an owned event.
- **Admin**: the highest role, used to maintain the application. Reads any account creedentials(except password) and detailed
event info. The only role that can change the role of another account.

## Events and bookings
### Event status policy
Allowed event status transitions: draft → active → locked → active → finished

Publishing can be only performed on a active event, never a draft. It cannot be reversed: withdrawing an event can be done by canceling it. Cancellation is reached through dedicated endpoint, since besides status change, it also cancel the current bookings as well.

### Event row lock
Operations on events are critical, therefore to avoid dozens of errors, row lock is implemented. Every operations that touches particular event row, first lock it using SELECT ... FOR UPDATE. Therefore the operations like: change event status or booking are quenued with any other that touch the same event.

### One active booking per user and event
A database index with unique(user_id, event_id) protects from booking same event twice. Booking cancelation drops the row out of the index, so the same user can book that event again.

### Cancelling an event cancels its bookings
The main reason why cancelation of an event has a separate endpoint, instaed by being covered by change status. Both event and all confirmed bookings on that event are cancelled in one transaction, since an error could leave confirmed bookings on a cancelled event, or otherwise.

### Booking policy

## API
### Uniform response envelope
Every answer carries `status`, `code`, `message` and `data`.

### Exception handlers
Custom exception handlers are configured, together with error logging. They also catch the 404 and 405 produced by FastAPI routing, when a route is not found or the method is not allowed.
This works because the handler is registered on the `HTTPException` imported from `starlette.exceptions` not the one from `fastapi.exceptions`.

Four handlers cover every way out of the application:

| Exception | Answer |
|---|---|
| `HTTPException` | the status code it was raised with, inside the envelope |
| `RequestValidationError` | 422, with the provided error fields in `data` |
| `ResponseValidationError` | 500, `RESPONSE_VALIDATION_ERROR` |
| `Exception` | 500, `INTERNAL_SERVER_ERROR` |

### ApiInfo, one vocabulary for codes and messages
Every code and message the API can return is declared once in `ApiInfo`, as an `ApiInfoItem` and has `CODE` and `MESSAGE`.

```python
USER_ALREADY_EXISTS = ApiInfoItem(
    CODE="USER_ALREADY_EXISTS",
    MESSAGE="User already exists.",
)
```

The same items feed both paths: a router passes the info to `ApiResponse.success`(fail or error) and `HTTPErrorItem` holds one as its `INFO`. The vocabulary of infos that a client sees lives in a single file.
The item is a frozen dataclass with slots=true, so a code and its message cannot be changed at runtime and no attribute can be added, even by accident.

### Predefined status codes and error info with an error factory
Every error is declared once as an `HTTPErrorItem`: a status code, a code and message pair, and optional headers. 

Raise them by calling:
```python
raise HTTPError.FORBIDDEN()
```

The call matters. Each raise builds a **new** `HTTPException`, rather than reusing a predefined instance, since an exception instance accumulates a traceback and a cause. This would make the logs contain the wrong level and a foreign traceback, and slowly leak RAM.

The factory also takes optional data, so a raised error can carry additional message. Example:
```python
raise HTTPError.INVALID_STATUS_TRANSITION(
    {
        "current": current_status,
        "allowed": sorted(current_status.next_statuses),
    }
)
```

## Data integrity
### Hashed password leak protection and custom HashedPassword ORM defined column type
A custom SQLAlchemy column type refuses anything but a hash on write and rebuilds it as a `HashedPassword` class on read. A plaintext row inserted by raw SQL will fail on the first read.

The password value travels between the functions as `HashedPassword`, a subclass of Pydantic's `SecretStr`, so it masks itself on e.x. __repr__ and inside log files. It is only unwrapped where the exact content is needed.

The `HashedPassword` constructor raises `ValueError` for anything the `PasswordHasher` class does not recognise as its own output. Therefore the class never contains a value that wasn't previously hashed with a known set of algorithms.

### UTC everywhere
The database, the containers and the tokens all operates exclusively on UTC and the application itself converts no timezones. Time conversion is left for an API Clinet. All date fields in request models are of `AwareTime`, therefore require additional time shift to be provided. Naive datatime objects raise an error, since database server will interpret naive datatime as UTC that will acctually corrupt data logic.

## Custom application tooling
### API internal CLI - `python -m app.cli`
That cli is one of appliation components, resides in `app/cli.py`. It currently holds one command, `create-bootstrap-admin`, which creates the first admin on boot, when the database has none and does nothing when one exists.

It reuses the db models, the settings and a session. The container entrypoint and `builder local up` both call it after the migrations.

### Static analysis
`ruff` and `mypy` run on every push in separate CI jobs, so a lint failure cannot hide a type error and so on.

read resource owned by someone else and
ones that does not exist end up with 404, so information about data present isn't leaking.
