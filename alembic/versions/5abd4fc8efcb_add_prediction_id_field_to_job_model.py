"""add prediction_id field to Job model

Revision ID: 5abd4fc8efcb
Revises: 169a794adb27
Create Date: 2025-07-24 15:27:31.686004+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5abd4fc8efcb'
down_revision: Union[str, None] = '169a794adb27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('jobs', sa.Column('prediction_id', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('jobs', 'prediction_id')
    # ### end Alembic commands ###
