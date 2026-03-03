"""merge heads

Revision ID: 1dd6991ed379
Revises: 001_change_validated_by, add_cabinet_agent_v1
Create Date: 2026-03-03 13:25:37.354382

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1dd6991ed379'
down_revision: Union[str, Sequence[str], None] = ('001_change_validated_by', 'add_cabinet_agent_v1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
