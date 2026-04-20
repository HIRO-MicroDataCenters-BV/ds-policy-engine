"""Create rules, metadata, and deploy_history tables.

Revision ID: 001
Revises: None
Create Date: 2026-04-02
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rules",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column("name", sa.String(200), unique=True, nullable=False),
        sa.Column("description", sa.Text(), default=""),
        sa.Column("role", sa.String(64), nullable=False, index=True),
        sa.Column(
            "institute",
            sa.String(64),
            nullable=False,
            server_default="",
            index=True,
        ),
        sa.Column("permissions_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.String(50), nullable=False),
        sa.Column("updated_at", sa.String(50), nullable=False),
    )

    op.create_table(
        "app_metadata",
        sa.Column("key", sa.String(50), primary_key=True),
        sa.Column("value", sa.Text(), nullable=True),
    )

    op.create_table(
        "deploy_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("deployed_at", sa.String(50), nullable=False, index=True),
        sa.Column(
            "deployed_by", sa.String(100), nullable=False, server_default="system"
        ),
        sa.Column("rules_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("roles_json", sa.Text(), nullable=False, server_default="[]"),
    )


def downgrade() -> None:
    op.drop_table("deploy_history")
    op.drop_table("app_metadata")
    op.drop_table("rules")
