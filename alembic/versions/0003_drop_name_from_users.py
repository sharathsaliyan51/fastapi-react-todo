"""drop name from users

Revision ID: 0003_drop_name_from_users
Revises: 0002_add_users_and_task_user_id
Create Date: 2026-05-19 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0003_drop_name_from_users"
down_revision = "0002_add_users_and_task_user_id"
branch_labels = None
depends_on = None


def _has_table(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _has_column(inspector: sa.Inspector, table_name: str, column_name: str) -> bool:
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _has_table(inspector, "users") and _has_column(inspector, "users", "name"):
        op.drop_column("users", "name")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _has_table(inspector, "users") and not _has_column(inspector, "users", "name"):
        op.add_column("users", sa.Column("name", sa.String(), nullable=True))
