"""
Create resumes_metadata table
Revision ID: 0004_resumes_metadata_table
Revises: 0003_rename_chat_columns
"""

from alembic import op
import sqlalchemy as sa


revision = "0004_resumes_metadata_table"
down_revision = "0003_rename_chat_columns"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Create the new resumes_metadata table
    op.create_table(
        "resumes_metadata",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id",sa.UUID(), nullable=False),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.Column("resume_name", sa.String(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("skills", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("experience_years", sa.Integer(), nullable=True),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("domain", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("resume_vector_id",sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("file_path", "resume_name", name="uq_file_path_resume_name"),
        sa.ForeignKey("user_id", "users.id", ondelete="CASCADE")
    )
    
    # Step 2: Update index names
    op.create_index("idx_resumes_metadata_user_id", "resumes_metadata", ["user_id"], unique=False)
    op.create_index("idx_resumes_metadata_file_path", "resumes_metadata", ["file_path"], unique=False)

def downgrade() -> None:
    
    # Drop the index on file_path
    op.drop_index("idx_resumes_metadata_file_path", table_name="resumes_metadata")
    # Drop the index on user_id
    op.drop_index("idx_resumes_metadata_user_id", table_name="resumes_metadata")

    # Drop the resumes_metadata table
    op.drop_table("resumes_metadata")