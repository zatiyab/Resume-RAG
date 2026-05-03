"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-05-02 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_name"), "users", ["name"], unique=False)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "chats",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chat_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("chat_id"),
    )
    op.create_index("idx_chats_user_id", "chats", ["user_id"], unique=False)

    op.create_table(
        "history",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hist_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("history", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("hist_id"),
    )
    op.create_index("idx_history_user_id", "history", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_history_user_id", table_name="history")
    op.drop_table("history")
    op.drop_index("idx_chats_user_id", table_name="chats")
    op.drop_table("chats")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index(op.f("ix_users_name"), table_name="users")
    op.drop_table("users")