# server

FastAPI + SQLAlchemy (async) + Alembic backend for `ds-policy-engine`.

Python 3.12, Poetry. Layout follows the [ds-catalog](https://github.com/HIRO-MicroDataCenters-BV/ds-catalog) template.

## Run

```bash
poetry install --with dev,test
cp .env.template .env
poetry run uvicorn app.main:app --reload --port 8000
```

## Layout

```
server/
├── alembic/                          # DB migrations
├── alembic.ini
├── app/
│   ├── main.py                       # FastAPI app + lifespan + routers
│   ├── settings.py                   # pydantic-settings (env prefix DS__)
│   ├── database.py                   # async engine, init_db, close_db, get_session_factory
│   ├── migrate_db.py                 # seed-from-JSON bootstrap (run on startup)
│   ├── conftest.py                   # root pytest fixtures (mock engine, in-memory repo, TestClient)
│   ├── core/                         # domain layer
│   │   ├── usecases.py               # I*Usecase ABCs + concrete impls
│   │   ├── validators.py             # validate_role / validate_permissions
│   │   ├── entities.py               # domain Pydantic types (re-exports HTTP shapes today)
│   │   ├── context.py                # Context dataclass (user / request_id / node_name)
│   │   ├── exceptions.py             # PolicyEngineError + subclasses
│   │   ├── constants.py              # default Role / Permission enums
│   │   ├── rego_generator.py         # PermissionBasedRegoStrategy + Protocol
│   │   ├── policy_engine.py          # PolicyEngine Protocol (OPA-agnostic)
│   │   ├── opa_adapter.py            # concrete OPA HTTP adapter
│   │   ├── repository/               # persistence layer
│   │   │   ├── repositories.py       # RuleRepository Protocol
│   │   │   ├── sqlite_rule_repository.py
│   │   │   └── db_models.py          # SQLAlchemy ORM (RuleRow, MetadataRow, DeployHistoryRow)
│   │   └── tests/                    # core unit tests (usecases, rego, repository, migrate_db)
│   └── rest_api/                     # HTTP layer
│       ├── depends.py                # FastAPI dependency wiring (get_*_usecase functions)
│       ├── response.py               # ApiResponse envelope + success/error helpers
│       ├── serializers.py            # request/response Pydantic schemas
│       └── routes/                   # one file per concern (policy, rules, health, …)
│           └── tests/                # integration tests (TestClient + DB + mock engine)
├── charts/ds-policy-engine/          # Helm chart (versioned, pushed to gh-pages by CI)
├── policies/                         # seed_rules.json (loaded by migrate_db on first run)
├── pyproject.toml                    # Poetry deps + tool configs (black/isort/pytest)
├── poetry.lock
├── Dockerfile
├── mypy.ini
├── .flake8
└── .env.template
```

## Linters

All four enforced via pre-commit and CI (`.github/workflows/server.yaml`):

```bash
poetry run mypy app
poetry run isort app --check --diff
poetry run flake8 app --config .flake8 --statistics
poetry run black app --check --diff
```

`mypy.ini` is the strict-but-pragmatic baseline ds-catalog uses; `.flake8` sets line-length = 88 with `E203, E704` ignored.

## Tests

Tests are colocated with the package they exercise:

```bash
poetry run pytest                   # all tests, picked up via testpaths = ["app"]
poetry run pytest app/core          # core unit tests only
poetry run pytest app/rest_api      # route/integration tests only
```

Routes use the FastAPI `TestClient` against a real SQLite file plus a mock policy engine (`MockPolicyEngine` in `conftest.py`).

## Database migrations

```bash
# generate a new migration after editing app/core/repository/db_models.py
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

`alembic/env.py` reads `DS__DATABASE_URL` (with fallback to `DATABASE_URL`).

## Configuration

All runtime knobs live in `app/settings.py` (pydantic-settings, env prefix `DS__`). See `.env.template` for the full list. Highlights:

| Var | Purpose |
|-----|---------|
| `DS__DATABASE_URL` | SQLAlchemy URL; SQLite default, Postgres works |
| `DS__OPA_BASE_URL` | OPA endpoint; `127.0.0.1:8181` in-pod (sidecar) |
| `DS__CORS_ALLOWED_ORIGINS` | Comma-separated origins; empty disables CORS middleware |
| `DS__DOCS_ENABLED` | `false` disables `/docs`, `/redoc`, `/openapi.json` |
| `DS__DB_QUERY_ENABLED` | `false` returns 403 on the ad-hoc `/api/v1/db/query` endpoint |
| `DS__POLICIES_DIR` | Path to seed rules dir (image default `/code/policies`) |
| `DS__NODE_NAME` | Site tag (`ki/hus/uva/local`); chart defaults from namespace |
