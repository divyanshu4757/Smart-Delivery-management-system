# 🚚 Smart Delivery Management System

**A geo-aware delivery orchestration backend** — from order creation to doorstep, with automatic driver matching and self-healing reassignment built in.

Built as a self-directed project to explore how delivery-logistics platforms actually solve dispatch: nearest-driver matching, hot-path location data, timeout-driven reassignment, and the operational edge cases that come with all three.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT-black?logo=jsonwebtokens)

---

## What it does

An admin onboards drivers. A delivery request comes in. The system finds the closest *available, capacity-eligible* driver to the warehouse, assigns the order, and gives them a window to respond. If they don't — or if they reject it — the system finds the next-best driver automatically, with no manual intervention. The driver tracks the order through pickup and delivery via a small state machine on both the order and the assignment.

That loop — **match → assign → timeout/reject → reassign** — is the core of the project.

---

## Architecture

```mermaid
flowchart LR
    Client["Client / Driver App"] -->|HTTPS + JWT| API["FastAPI"]
    API -->|orders, drivers, assignments<br/>source of truth| PG[("PostgreSQL")]
    API -->|live GPS pings| Redis[("Redis")]
    API -->|distance lookups| Redis
    Scheduler["APScheduler<br/>(expiry + rejection jobs)"] -->|poll every 5s| PG
    Scheduler -->|reassign on timeout/rejection| PG
```

The split between Postgres and Redis is deliberate, not incidental:

- **Postgres** holds everything that needs to be durable and queryable — orders, drivers, assignments, their full history.
- **Redis** holds only the one thing that changes constantly and doesn't need history: a driver's *current* lat/lng. Pushing every GPS ping into Postgres would mean constant writes to a row something else is also trying to read and lock; Redis takes that churn off the relational store entirely.

Two background jobs poll Postgres every 5 seconds, independent of any incoming request, and handle the cases where a driver doesn't respond in time:

- **`expired_assignments`** — picks up any `PENDING` assignment past its 3-minute window, finds the next-closest available driver, and reassigns.
- **`rejected_assignments`** — picks up `REJECTED` assignments, excludes every driver who's already turned that order down, and reassigns from the remaining pool.

---

## State machines

**Order**

```mermaid
stateDiagram-v2
    [*] --> CREATED
    CREATED --> ASSIGNED: driver accepts assignment
    ASSIGNED --> PICKED_UP: driver picks up
    PICKED_UP --> DELIVERED: driver delivers
    CREATED --> EXCEPTION: no eligible driver found
    ASSIGNED --> EXCEPTION: reassignment pool exhausted
```
*(`ADDRESS_VERIFICATION_PENDING` is defined on the model as a reserved future state — not yet wired into the live flow.)*

**Assignment**

```mermaid
stateDiagram-v2
    [*] --> PENDING
    PENDING --> ACCEPTED: driver accepts
    PENDING --> REJECTED: driver rejects
    PENDING --> EXPIRED: 3-minute timeout (background job)
    REJECTED --> [*]: order reassigned, excluding this driver
    EXPIRED --> [*]: order reassigned
```

---

## How driver matching works

When an order is created:

1. Query every driver who is `available`, has enough `max_capacity_kg` for the order's weight, and operates out of a city served by the order's warehouse.
2. For each candidate, pull their **live** location from Redis and compute the great-circle distance to the warehouse via the **Haversine formula**.
3. Sort by distance, assign to the closest, open a 3-minute response window.

Distance is calculated driver → *warehouse*, not driver → delivery address — the driver has to pick up the order before they can deliver it, so that's the leg that actually determines response time.

---

## Tech stack

| Layer | Choice |
|---|---|
| API framework | FastAPI |
| Database | PostgreSQL via SQLAlchemy ORM |
| Hot-path store | Redis (live driver location) |
| Auth | JWT (`python-jose`) + bcrypt password hashing (`passlib`) |
| Background jobs | APScheduler |
| Geo distance | Haversine |
| Validation | Pydantic v2 |
| Testing | pytest, isolated SQLite test DB, in-memory Redis fake |

---

## Project structure

```
.
├── main.py                       # app entrypoint — wires routers + schedulers
├── database.py                   # SQLAlchemy engine/session setup
├── models/                       # ORM models
│   ├── users.py                  # auth identity, role (ADMIN/DRIVER)
│   ├── drivers.py                # driver profile, vehicle, capacity
│   ├── warehouses.py / cities.py
│   ├── orders.py                 # order + OrderStatus state machine
│   └── assignments.py            # order↔driver assignment + AssignmentStatus
├── routes/
│   ├── admin.py                  # login, create_driver, JWT issuing/validation
│   ├── drivers.py                # shift mgmt, location push, accept/reject
│   └── order.py                  # order creation, nearest-driver matching, pickup/deliver
├── pydanticValidations/          # request schemas, separate from ORM models
├── jobs/
│   ├── expired_assignments.py    # timeout-driven reassignment
│   └── rejected_assignments.py   # rejection-driven reassignment
└── tests/                        # pytest suite
```

---

## API reference

### Auth — `/auth`

| Method | Endpoint | Role | Description |
|---|---|---|---|
| POST | `/auth/login` | — | OAuth2 password login, returns a JWT |
| POST | `/auth/create_driver` | Admin | Creates a `User` + `Driver` profile in one transaction |

### Driver operations — `/drivers`

| Method | Endpoint | Role | Description |
|---|---|---|---|
| POST | `/drivers/driver_location` | Driver | Pushes live lat/lng to Redis |
| PUT | `/drivers/start_shift` | Driver | Marks driver available |
| PUT | `/drivers/end_shift` | Driver | Marks driver unavailable |
| GET | `/drivers/my_assignments` | Driver | Lists this driver's pending assignments |
| POST | `/drivers/accept_assignment/{id}` | Driver | Accepts; order moves to `ASSIGNED` |
| POST | `/drivers/reject_assignment/{id}` | Driver | Rejects; picked up by the rejection job |

### Order operations — `/order`

| Method | Endpoint | Role | Description |
|---|---|---|---|
| POST | `/order/create_order` | — | Creates an order, auto-assigns the nearest eligible driver |
| PUT | `/order/pickup_order/{id}` | Driver | Marks order `PICKED_UP` |
| PUT | `/order/deliver_order/{id}` | Driver | Marks order `DELIVERED` |

---

## Getting started

**Prerequisites:** Python 3.12+, a running PostgreSQL instance, a running Redis instance.

```bash
git clone <repo-url>
cd "Smart Delivery management system"

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install fastapi uvicorn sqlalchemy python-dotenv passlib bcrypt \
            python-jose redis haversine apscheduler python-multipart
```

Create a `.env` in the project root:

| Variable | Description |
|---|---|
| `DATABASE_URL` | SQLAlchemy connection string, e.g. `postgresql://user:pass@localhost:5432/sdms` |
| `SECRET_KEY` | JWT signing secret — generate with `openssl rand -hex 32` |
| `ALGORITHM` | JWT signing algorithm, e.g. `HS256` |

Run it:

```bash
uvicorn main:app --reload
```

Interactive API docs at `http://localhost:8000/docs`.

---

## Testing

```bash
pip install pytest python-multipart
python -m pytest tests/ -v
```

28 tests covering auth and role checks, shift management, the full order lifecycle (create → match → accept → pickup → deliver), and both background reassignment jobs — including their `EXCEPTION` fallback paths when no driver is left to assign. Runs against an isolated SQLite database and an in-memory Redis fake; no external services required.

---

## Known limitations

Documented intentionally rather than discovered later:

- **No row-level locking** between the accept/reject endpoints and the background expiry job — a driver accepting at the exact moment their assignment expires can produce an inconsistent state. Fix: `SELECT ... FOR UPDATE` around the read-modify-write.
- **No composite index on `assignments(status, expires_at)`** — the exact predicate the 5-second poller filters on. Fine at current scale, becomes a full table scan as data grows.
- **`get_available_drivers` filters on `Driver.latitude`/`longitude` (Postgres columns)**, but no route currently writes to them — only Redis receives live location updates. Driver eligibility currently depends on those columns being seeded some other way.
- **In-process `APScheduler`** doesn't survive horizontal scaling — running multiple app instances would duplicate-process the same expired/rejected assignments. A distributed setup (Celery beat + worker, or a leader-elected lock) would be the next step.
- **`/order/create_order` has no auth requirement** — fine for local development, would need an internal-service auth layer before any real exposure.
- **No pinned `requirements.txt` yet.**

---

## License

MIT — use freely as a reference or starting point.
