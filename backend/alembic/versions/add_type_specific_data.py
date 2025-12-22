"""Add type_specific_data and answer_data columns

Revision ID: add_type_specific_data
Revises: e84a85e465b8
Create Date: 2025-12-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_type_specific_data'
down_revision: Union[str, None] = 'e84a85e465b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add type_specific_data and answer_data to listening_questions
    op.add_column('listening_questions', sa.Column('type_specific_data', sa.JSON(), nullable=True))
    op.add_column('listening_questions', sa.Column('answer_data', sa.JSON(), nullable=True))
    
    # Add type_specific_data, answer_data, and image_url to reading_questions
    op.add_column('reading_questions', sa.Column('type_specific_data', sa.JSON(), nullable=True))
    op.add_column('reading_questions', sa.Column('answer_data', sa.JSON(), nullable=True))
    op.add_column('reading_questions', sa.Column('image_url', sa.String(500), nullable=True))


def downgrade() -> None:
    # Remove columns from reading_questions
    op.drop_column('reading_questions', 'image_url')
    op.drop_column('reading_questions', 'answer_data')
    op.drop_column('reading_questions', 'type_specific_data')
    
    # Remove columns from listening_questions
    op.drop_column('listening_questions', 'answer_data')
    op.drop_column('listening_questions', 'type_specific_data')
