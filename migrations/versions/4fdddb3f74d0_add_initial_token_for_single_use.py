"""Add initial token for single use

Revision ID: 4fdddb3f74d0
Revises: 378fa8da1d0b
Create Date: 2020-04-08 03:37:07.656329

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4fdddb3f74d0'
down_revision = '378fa8da1d0b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('attendee', sa.Column('initial_token', sa.String(length=50), nullable=True))
    op.create_unique_constraint(None, 'attendee', ['initial_token'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'attendee', type_='unique')
    op.drop_column('attendee', 'initial_token')
    # ### end Alembic commands ###
