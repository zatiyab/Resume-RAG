"""Drop domain column from resumes

Revision ID: b3f1c4a9d002
Revises: 84777312b323
Create Date: 2026-05-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3f1c4a9d002'
down_revision: Union[str, None] = '84777312b323'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('resumes', 'domain')


def downgrade() -> None:
    op.add_column('resumes', sa.Column('domain', sa.ARRAY(sa.VARCHAR(length=255)), nullable=True))
