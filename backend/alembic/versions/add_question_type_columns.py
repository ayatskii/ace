"""add_question_type_columns

Revision ID: add_question_type_columns
Revises: 
Create Date: 2025-12-22 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_question_type_columns'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Listening Questions
    op.add_column('listening_questions', sa.Column('type_specific_data', sa.JSON(), nullable=True))
    op.add_column('listening_questions', sa.Column('answer_data', sa.JSON(), nullable=True))
    op.add_column('listening_questions', sa.Column('options', sa.JSON(), nullable=True))

    # Reading Questions
    op.add_column('reading_questions', sa.Column('type_specific_data', sa.JSON(), nullable=True))
    op.add_column('reading_questions', sa.Column('answer_data', sa.JSON(), nullable=True))
    op.add_column('reading_questions', sa.Column('options', sa.JSON(), nullable=True))


def downgrade() -> None:
    # Listening Questions
    op.drop_column('listening_questions', 'options')
    op.drop_column('listening_questions', 'answer_data')
    op.drop_column('listening_questions', 'type_specific_data')

    # Reading Questions
    op.drop_column('reading_questions', 'options')
    op.drop_column('reading_questions', 'answer_data')
    op.drop_column('reading_questions', 'type_specific_data')
