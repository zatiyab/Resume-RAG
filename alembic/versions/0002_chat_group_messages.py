"""chat group message ids

Revision ID: 0002_chat_group_messages
Revises: 0001_initial_schema
Create Date: 2026-05-04 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


revision = "0002_chat_group_messages"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "chats",
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    connection = op.get_bind()
    chat_rows = connection.execute(sa.text("SELECT chat_id FROM chats")).fetchall()
    for row in chat_rows:
        connection.execute(
            sa.text("UPDATE chats SET message_id = :message_id WHERE chat_id = :chat_id"),
            {"message_id": str(uuid.uuid4()), "chat_id": row.chat_id},
        )

    op.alter_column("chats", "message_id", nullable=False)
    op.drop_constraint("chats_pkey", "chats", type_="primary")
    op.create_primary_key("pk_chats_message_id", "chats", ["message_id"])
    op.create_index("idx_chats_chat_id", "chats", ["chat_id"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_chats_chat_id", table_name="chats")
    op.drop_constraint("pk_chats_message_id", "chats", type_="primary")
    op.create_primary_key("chats_pkey", "chats", ["chat_id"])
    op.drop_column("chats", "message_id")
