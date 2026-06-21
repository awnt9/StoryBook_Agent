"""create user api keys

Revision ID: f28b5d730a41
Revises: e4f6a82d3c19
Create Date: 2026-06-20 00:00:00.000000

"""
import os
from datetime import datetime
from typing import Sequence, Union

from alembic import op
from cryptography.fernet import Fernet
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f28b5d730a41"
down_revision: Union[str, Sequence[str], None] = "e4f6a82d3c19"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _cipher() -> Fernet:
    encryption_key = os.getenv("API_KEY_ENCRYPTION_KEY")
    if not encryption_key:
        raise RuntimeError(
            "API_KEY_ENCRYPTION_KEY is required to migrate stored API keys"
        )
    return Fernet(encryption_key.encode("utf-8"))


def upgrade() -> None:
    op.create_table(
        "user_api_keys",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=100), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("encrypted_key", sa.String(length=2048), nullable=False),
        sa.Column("last_four", sa.String(length=4), nullable=False),
        sa.Column("is_selected", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_api_keys_id"),
        "user_api_keys",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_api_keys_user_id"),
        "user_api_keys",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "uq_user_api_keys_selected",
        "user_api_keys",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("is_selected"),
    )

    connection = op.get_bind()
    users = connection.execute(
        sa.text("SELECT id, api_key FROM users WHERE api_key IS NOT NULL")
    ).mappings()
    existing_keys = list(users)

    if existing_keys:
        cipher = _cipher()
        now = datetime.utcnow()
        for user in existing_keys:
            plain_key = user["api_key"].strip()
            if not plain_key:
                continue
            connection.execute(
                sa.text(
                    """
                    INSERT INTO user_api_keys
                        (user_id, label, provider, encrypted_key, last_four,
                         is_selected, created_at, updated_at)
                    VALUES
                        (:user_id, :label, :provider, :encrypted_key, :last_four,
                         true, :created_at, :updated_at)
                    """
                ),
                {
                    "user_id": user["id"],
                    "label": "Imported key",
                    "provider": "openai",
                    "encrypted_key": cipher.encrypt(
                        plain_key.encode("utf-8")
                    ).decode("utf-8"),
                    "last_four": plain_key[-4:],
                    "created_at": now,
                    "updated_at": now,
                },
            )

    op.drop_column("users", "api_key")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("api_key", sa.String(length=512), nullable=True),
    )

    connection = op.get_bind()
    selected_keys = list(
        connection.execute(
            sa.text(
                """
                SELECT user_id, encrypted_key
                FROM user_api_keys
                WHERE is_selected = true
                """
            )
        ).mappings()
    )
    if selected_keys:
        cipher = _cipher()
        for stored_key in selected_keys:
            plain_key = cipher.decrypt(
                stored_key["encrypted_key"].encode("utf-8")
            ).decode("utf-8")
            connection.execute(
                sa.text("UPDATE users SET api_key = :api_key WHERE id = :user_id"),
                {"api_key": plain_key, "user_id": stored_key["user_id"]},
            )

    op.drop_index("uq_user_api_keys_selected", table_name="user_api_keys")
    op.drop_index(op.f("ix_user_api_keys_user_id"), table_name="user_api_keys")
    op.drop_index(op.f("ix_user_api_keys_id"), table_name="user_api_keys")
    op.drop_table("user_api_keys")
