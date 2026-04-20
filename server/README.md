# server

FastAPI + SQLAlchemy (async) + Alembic backend for `ds-policy-engine`.

Python 3.12, Poetry.

## Run

```bash
poetry install --with dev,test
cp .env.template .env
poetry run uvicorn app.main:app --reload --port 8000
```

## Layout

```
server/
├── alembic/            # DB migrations
├── alembic.ini
├── app/
│   ├── main.py         # FastAPI app
│   ├── config.py       # pydantic-settings (env prefix DS__)
│   ├── core/           # exceptions, dependencies, constants
│   ├── db/             # engine, models, seed
│   ├── adapters/       # OPA HTTP adapter
│   ├── repositories/   # SQLAlchemy repositories
│   ├── services/       # domain services
│   ├── models/         # Pydantic request/response schemas
│   └── routes/         # FastAPI routers
├── charts/ds-policy-engine/   # Helm chart
├── policies/           # Rego seed
└── tests/              # unit + integration
```

## Linters

All enforced via pre-commit and CI:
- `black` (formatter, line length 88)
- `isort`
- `flake8` (config: `.flake8`)
- `mypy` (config: `mypy.ini`)

## DB migrations

```bash
# generate a new migration after changing app/db/models.py
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```
