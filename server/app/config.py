"""
Application configuration via environment variables.

Uses pydantic-settings with env_prefix DS__ (HIRO convention).
All env vars read by this service start with ``DS__``.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- OPA connection ---
    opa_base_url: str = "http://ds-opa:8181"
    opa_timeout: float = 3.0
    opa_policy_path: str = "ds/authz/decision"

    # --- Paths ---
    policies_dir: str = "/code/policies"

    # --- Server metadata ---
    log_level: str = "INFO"
    app_version: str = "0.1.0"
    node_name: str = "local"

    # --- Database ---
    # SQLite default; swap to PostgreSQL via:
    #   postgresql+asyncpg://user:pass@host:5432/dbname
    database_url: str = "sqlite+aiosqlite:////app/data/policy_engine.db"

    # --- CORS ---
    # Comma-separated list of origins allowed to call the API.
    # Empty => CORS middleware not installed.
    cors_allowed_origins: str = ""

    # --- Docs ---
    # When false, /docs, /redoc, /openapi.json are disabled.
    docs_enabled: bool = True

    # --- DB query endpoint ---
    # Gates /api/v1/db/query (arbitrary read-only SELECT). Off by default —
    # even SELECT-only endpoints are a data-exfiltration + DoS surface if
    # exposed to unauthenticated callers. Enable only in dev/debug.
    db_query_enabled: bool = False

    model_config = SettingsConfigDict(
        env_prefix="DS__",
        env_file=".env",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS allowed origins as a list (split on comma, trim empties)."""
        if not self.cors_allowed_origins.strip():
            return []
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]


settings = Settings()
