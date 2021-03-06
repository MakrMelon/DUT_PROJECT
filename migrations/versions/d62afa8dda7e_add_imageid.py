"""add imageid

Revision ID: d62afa8dda7e
Revises: 2e690e1997b5
Create Date: 2017-05-17 00:12:30.995220

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd62afa8dda7e'
down_revision = '2e690e1997b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('image_id', sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'image_id')
    # ### end Alembic commands ###
