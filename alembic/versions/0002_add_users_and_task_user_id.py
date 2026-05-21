"""add users table and task user ownership

Revision ID: 0002_add_users_and_task_user_id
Revises: 0001_create_or_update_tasks
Create Date: 2026-05-18 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_add_users_and_task_user_id"
down_revision = "0001_create_or_update_tasks"
branch_labels = None
depends_on = None


LEGACY_USERNAME = "legacy_user"
LEGACY_NAME = "Legacy User"
LEGACY_EMAIL = "legacy@example.com"
LEGACY_PASSWORD_HASH = "legacy-imported-no-login"


def _has_table(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _has_column(inspector: sa.Inspector, table_name: str, column_name: str) -> bool:
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _has_foreign_key(inspector: sa.Inspector, table_name: str, constraint_name: str) -> bool:
    return constraint_name in {
        constraint["name"] for constraint in inspector.get_foreign_keys(table_name)
    }


def _has_index(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def _has_unique_constraint(
    inspector: sa.Inspector, table_name: str, constraint_name: str
) -> bool:
    return constraint_name in {
        constraint["name"] for constraint in inspector.get_unique_constraints(table_name)
    }


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _has_table(inspector, "users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("username", sa.String(), nullable=False),
            sa.Column("email", sa.String(), nullable=False),
            sa.Column("password_hash", sa.String(), nullable=False),
            sa.UniqueConstraint("username", name="uq_users_username"),
            sa.UniqueConstraint("email", name="uq_users_email"),
        )
        op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    else:
        if not _has_column(inspector, "users", "id"):
            op.add_column("users", sa.Column("id", sa.Integer(), nullable=True))

        if not _has_column(inspector, "users", "username"):
            op.add_column("users", sa.Column("username", sa.String(), nullable=True))

        if not _has_column(inspector, "users", "email"):
            op.add_column("users", sa.Column("email", sa.String(), nullable=True))

        if not _has_column(inspector, "users", "password_hash"):
            op.add_column("users", sa.Column("password_hash", sa.String(), nullable=True))

        users = sa.table(
            "users",
            sa.column("id", sa.Integer()),
            sa.column("username", sa.String()),
            sa.column("email", sa.String()),
            sa.column("password_hash", sa.String()),
        )

        existing_users = bind.execute(
            sa.select(
                users.c.id,
                users.c.username,
                users.c.email,
                users.c.password_hash,
            )
        ).mappings()
        for index, user in enumerate(existing_users, start=1):
            user_key = user["id"] or index
            values = {}
            if not user["username"]:
                values["username"] = f"{LEGACY_USERNAME}_{user_key}"
            if not user["email"]:
                values["email"] = f"legacy+{user_key}@example.com"
            if not user["password_hash"]:
                values["password_hash"] = LEGACY_PASSWORD_HASH

            if values:
                bind.execute(
                    users.update()
                    .where(users.c.id == user["id"])
                    .values(**values)
                )

        op.alter_column("users", "username", existing_type=sa.String(), nullable=False)
        op.alter_column("users", "email", existing_type=sa.String(), nullable=False)
        op.alter_column(
            "users", "password_hash", existing_type=sa.String(), nullable=False
        )

        inspector = sa.inspect(bind)
        if not _has_unique_constraint(inspector, "users", "uq_users_username"):
            op.create_unique_constraint("uq_users_username", "users", ["username"])
        if not _has_unique_constraint(inspector, "users", "uq_users_email"):
            op.create_unique_constraint("uq_users_email", "users", ["email"])
        if not _has_index(inspector, "users", "ix_users_id"):
            op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    inspector = sa.inspect(bind)
    if not _has_table(inspector, "tasks"):
        return

    if not _has_column(inspector, "tasks", "user_id"):
        op.add_column("tasks", sa.Column("user_id", sa.Integer(), nullable=True))

    user_columns = [
        sa.column("id", sa.Integer()),
        sa.column("username", sa.String()),
        sa.column("email", sa.String()),
        sa.column("password_hash", sa.String()),
    ]
    users_has_name = _has_column(inspector, "users", "name")
    if users_has_name:
        user_columns.append(sa.column("name", sa.String()))

    users = sa.table("users", *user_columns)
    tasks = sa.table("tasks", sa.column("user_id", sa.Integer()))

    legacy_user_id = bind.execute(
        sa.select(users.c.id).where(users.c.username == LEGACY_USERNAME)
    ).scalar_one_or_none()

    if legacy_user_id is None:
        legacy_user_values = {
            "username": LEGACY_USERNAME,
            "email": LEGACY_EMAIL,
            "password_hash": LEGACY_PASSWORD_HASH,
        }
        if users_has_name:
            legacy_user_values["name"] = LEGACY_NAME

        result = bind.execute(
            users.insert()
            .values(**legacy_user_values)
            .returning(users.c.id)
        )
        legacy_user_id = result.scalar_one()

    bind.execute(
        tasks.update()
        .where(tasks.c.user_id.is_(None))
        .values(user_id=legacy_user_id)
    )

    op.alter_column("tasks", "user_id", existing_type=sa.Integer(), nullable=False)

    inspector = sa.inspect(bind)
    if not _has_foreign_key(inspector, "tasks", "fk_tasks_user_id_users"):
        op.create_foreign_key(
            "fk_tasks_user_id_users",
            "tasks",
            "users",
            ["user_id"],
            ["id"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _has_table(inspector, "tasks"):
        if _has_foreign_key(inspector, "tasks", "fk_tasks_user_id_users"):
            op.drop_constraint("fk_tasks_user_id_users", "tasks", type_="foreignkey")

        inspector = sa.inspect(bind)
        if _has_column(inspector, "tasks", "user_id"):
            op.drop_column("tasks", "user_id")

    inspector = sa.inspect(bind)
    if _has_table(inspector, "users"):
        op.drop_index(op.f("ix_users_id"), table_name="users")
        op.drop_table("users")
