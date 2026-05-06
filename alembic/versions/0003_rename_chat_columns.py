"""rename chat columns for clarity

Revision ID: 0003_rename_chat_columns
Revises: 0002_chat_group_messages
Create Date: 2026-05-04 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_rename_chat_columns"
down_revision = "0002_chat_group_messages"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Rename existing chat_id to chat_group_id first (to avoid conflicts)
    op.alter_column("chats", "chat_id", new_column_name="chat_group_id")
    
    # Step 2: Rename message_id to chat_id (primary key)
    op.alter_column("chats", "message_id", new_column_name="chat_id")
    
    # Step 3: Update the primary key constraint name
    op.drop_constraint("pk_chats_message_id", "chats", type_="primary")
    op.create_primary_key("pk_chats_chat_id", "chats", ["chat_id"])
    
    # Step 4: Update index names
    op.drop_index("idx_chats_chat_id", table_name="chats")
    op.create_index("idx_chats_chat_group_id", "chats", ["chat_group_id"], unique=False)


def downgrade() -> None:
    # Revert index changes
    op.drop_index("idx_chats_chat_group_id", table_name="chats")
    op.create_index("idx_chats_chat_id", "chats", ["chat_id"], unique=False)
    
    # Drop primary key and recreate with old name
    op.drop_constraint("pk_chats_chat_id", "chats", type_="primary")
    op.create_primary_key("pk_chats_message_id", "chats", ["message_id"])
    
    # Rename columns back
    op.alter_column("chats", "chat_group_id", new_column_name="chat_id")
    op.alter_column("chats", "chat_id", new_column_name="message_id")
