"""empty message

Revision ID: 8680f5fa40b2
Revises: 9ecb3d5d37f8
Create Date: 2017-02-15 14:23:16.322358

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8680f5fa40b2'
down_revision = '9ecb3d5d37f8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('body_html', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'body_html')
    # ### end Alembic commands ###