"""initial schema

Revision ID: bc22ff667c17
Revises:
Create Date: 2026-07-31 14:56:16.307988
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bc22ff667c17"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "username",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "hashed_password",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )

    op.create_index(
        "ix_users_id",
        "users",
        ["id"],
        unique=False,
    )

    op.create_table(
        "files",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "original_name",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "stored_name",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "file_path",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "content_type",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "size",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "owner_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stored_name"),
    )

    op.create_index(
        "ix_files_id",
        "files",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_files_id",
        table_name="files",
    )

    op.drop_table("files")

    op.drop_index(
        "ix_users_id",
        table_name="users",
    )

    op.drop_table("users")