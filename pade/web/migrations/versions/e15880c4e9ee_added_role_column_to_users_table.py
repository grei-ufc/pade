"""added role column to users table

Revision ID: e15880c4e9ee
Revises: 
Create Date: 2018-11-14 23:23:49.252127

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e15880c4e9ee'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('role', sa.String(length=32), nullable=True))


def downgrade():
    op.drop_column('users', 'role')
