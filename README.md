# aptiview_observability

A production-safe Django observability service that monitors HTTP, Redis, and Postgres dependencies and exposes consolidated health status via API.

## Stack

- Python 3.11 (Docker runtime)
- Django
- Django REST Framework
- PostgreSQL
- Redis

## Features

- Service registry (`Service`)
- Latest service status (`ServiceStatus`)
- Modular check framework:
  - HTTP check
  - Redis check
  - DB check
- Polling worker (`run_checks`) every 60 seconds
- Health API: `GET /api/status/`
- History API: `GET /api/status/history/`
- Admin management for services and statuses
- Seed command for initial monitored services

## Project Structure

```text
aptiview_observability/
├── aptiview_observability/
│   ├── settings.py
│   └── urls.py
├── observability/
│   ├── checks/
│   │   ├── base.py
│   │   ├── http_check.py
│   │   ├── redis_check.py
│   │   └── db_check.py
│   ├── management/commands/
│   │   ├── run_checks.py
│   │   └── seed_services.py
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py
```

## Environment Variables

Use env vars for all infra configuration. No DB/Redis credentials are hardcoded in app logic.

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG` (`True` / `False`)
- `DJANGO_ALLOWED_HOSTS` (comma-separated)
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `REDIS_HOST`
- `REDIS_PORT`
- `SERVICE_BACKEND_ENDPOINT` (default: `https://dev.aptiview.com/healthz`)
- `SERVICE_REDIS_ENDPOINT` (optional)
- `SERVICE_POSTGRES_ENDPOINT` (optional)

If `DB_NAME` is not set, app falls back to SQLite for local quick start.
Service endpoint env vars are applied when running `seed_services`.
The app auto-loads `.env` via `python-dotenv`, so restarting Django/worker is enough for local env values to be picked up.

## Local Setup

From the `aptiview_observability` directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Run migrations:

```bash
.venv/bin/python manage.py makemigrations observability
.venv/bin/python manage.py migrate
```

Seed initial services:

```bash
.venv/bin/python manage.py seed_services
```

Start API server:

```bash
.venv/bin/python manage.py runserver
```

Start worker (separate terminal):

```bash
.venv/bin/python manage.py run_checks
```

## Docker Setup

From the `aptiview_observability` directory:

```bash
docker compose up --build
```

This starts:

- `observability` (Django API)
- `observability-worker` (checks loop)
- `Database Service`
- `Caching Service`

## API

Rate limit: status endpoints are limited to `10 requests/minute` per client IP.

### GET `/api/status/`

Example response:

```json
{
  "overall_status": "operational",
  "services": [
    {
      "name": "Aptiview API",
      "status": "operational",
      "latency": 120,
      "message": "OK"
    }
  ]
}
```

Includes incident metadata:

- current open incident id + start time
- last incident end time

### GET `/api/status/history/`

Returns latest status timeline entries across services.
Optional query param: `limit` (default 100, max 500).

Overall status logic:

- If any `critical` service is `outage` => overall is `outage`
- Else if any service is `degraded` => overall is `degraded`
- Else if any `non_critical` service is `outage` => overall is `degraded`
- Else => `operational`

## Status Semantics

Each service transitions through states based on consecutive check results:

- `operational` -> service is healthy
- `degraded` -> transient failure (for example, first failed check)
- `outage` -> confirmed failure (2+ consecutive failures)

Hysteresis is used to prevent flapping:

- `outage` is set only after multiple consecutive failures
- Recovery to `operational` requires multiple consecutive successes

## Service Criticality

Each service has `criticality`:

- `critical`
- `non_critical`

Seed defaults:

- `Aptiview API` -> `critical`
- `Database Service` -> `critical`
- `Caching Service` -> `non_critical`

## Incident Tracking

Incidents are modeled explicitly:

- `start_time`
- `end_time`
- `affected_services`

Lifecycle:

- incident opens when any service transitions into `outage`
- incident closes when no services remain in `outage`

## Health Check Behavior

### HTTP checks

- `200` with valid response -> `operational`
- `4xx` -> `degraded`
- `5xx` / timeout / DNS failure -> `outage`
- JSON response with `"status" != "ok"` -> failure

### Redis check

- Successful ping -> `operational`
- Failure -> `outage`

### Postgres check

- Successful `SELECT 1` -> `operational`
- Failure -> `outage`

## Error Message Normalization

Raw internal exceptions are normalized before storing in `ServiceStatus.message`:

- DNS resolution errors -> `DNS resolution failed`
- Timeout errors -> `Request timed out`
- Connection errors -> `Connection failed`

## Stability Mechanism (Hysteresis)

- 1st consecutive failure -> `degraded`
- 2nd consecutive failure -> `outage`
- 1st consecutive success after degradation/outage -> unchanged state
- 2nd consecutive success -> `operational`

## Concurrency Notes

`run_checks` uses database transactions and row-level locking (`select_for_update`) when updating service status. This reduces race conditions for multi-worker deployments, though a dedicated distributed lock can be added later for stricter singleton scheduling.

## Useful Commands

Check project health:

```bash
.venv/bin/python manage.py check
```

Create superuser:

```bash
.venv/bin/python manage.py createsuperuser
```

Admin panel:

- URL: `http://127.0.0.1:8000/admin/`

## Validation / Testing

Test API endpoint:

```bash
curl -s http://127.0.0.1:8000/api/status/ | python -m json.tool
```

Watch health updates:

```bash
watch -n 5 "curl -s http://127.0.0.1:8000/api/status/ | python -m json.tool"
```
