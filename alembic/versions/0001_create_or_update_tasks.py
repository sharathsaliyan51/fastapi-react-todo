"""create or update tasks table

Revision ID: 0001_create_or_update_tasks
Revises:
Create Date: 2026-04-26 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_create_or_update_tasks"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = inspector.get_table_names()

    if "tasks" not in table_names:
        op.create_table(
            "tasks",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("title", sa.String(), nullable=False),
            sa.Column("description", sa.String(), nullable=False),
            sa.Column("date", sa.Date(), nullable=False),
            sa.Column("status", sa.String(), nullable=False, server_default="todo"),
        )
        op.create_index(op.f("ix_tasks_id"), "tasks", ["id"], unique=False)
        return

    columns = {column["name"] for column in inspector.get_columns("tasks")}
    if "status" not in columns:
        op.add_column(
            "tasks",
            sa.Column("status", sa.String(), nullable=False, server_default="todo"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = inspector.get_table_names()
    if "tasks" not in table_names:
        return

    columns = {column["name"] for column in inspector.get_columns("tasks")}
    if "status" in columns:
        op.drop_column("tasks", "status")
