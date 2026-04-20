"""
SQLAlchemy ORM models.

All database tables are defined here. Alembic uses these models
for autogenerate migrations. To add a new table:
  1. Define a new class inheriting from Base
  2. Run: alembic revision --autogenerate -m "add <table> table"
  3. Run: alembic upgrade head
"""

import json

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models."""

    pass


class RuleRow(Base):
    """Policy rule stored in the database."""

    __tablename__ = "rules"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    role: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    institute: Mapped[str] = mapped_column(String(64), nullable=False, default="", index=True)
    permissions_json: Mapped[str] = mapped_column(
        Text, nullable=False, default="[]"
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[str] = mapped_column(String(50), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(50), nullable=False)

    @property
    def permissions(self) -> list[str]:
        """Deserialize permissions from JSON string."""
        return json.loads(self.permissions_json)

    @permissions.setter
    def permissions(self, value: list[str]) -> None:
        """Serialize permissions to JSON string."""
        self.permissions_json = json.dumps(value)


class MetadataRow(Base):
    """Key-value metadata (version, last_deployed, etc.)."""

    __tablename__ = "app_metadata"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    value: Mapped[str | None] = mapped_column(Text)


class DeployHistoryRow(Base):
    """Individual deploy history entry."""

    __tablename__ = "deploy_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    version: Mapped[int] = mapped_column(nullable=False)
    deployed_at: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    deployed_by: Mapped[str] = mapped_column(String(100), nullable=False, default="system")
    rules_count: Mapped[int] = mapped_column(nullable=False, default=0)
    roles_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    @property
    def roles(self) -> list[str]:
        return json.loads(self.roles_json)

    @roles.setter
    def roles(self, value: list[str]) -> None:
        self.roles_json = json.dumps(value)
