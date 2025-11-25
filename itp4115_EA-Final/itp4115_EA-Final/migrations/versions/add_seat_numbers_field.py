"""add seat_numbers to ticket model

Revision ID: a1b2c3d4e5f6
Revises: f1a16545eaa6
Create Date: 2025-11-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'f1a16545eaa6'
branch_labels = None
depends_on = None


def upgrade():
    # Add seat_numbers column to ticket table
    op.add_column('ticket', sa.Column('seat_numbers', sa.String(length=256), nullable=True))


def downgrade():
    # Remove seat_numbers column from ticket table
    op.drop_column('ticket', 'seat_numbers')
