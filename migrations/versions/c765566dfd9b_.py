"""empty message

Revision ID: c765566dfd9b
Revises: 5ecd4056d9bb
Create Date: 2017-05-19 07:44:24.121731

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c765566dfd9b'
down_revision = '5ecd4056d9bb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('Htitle', sa.Text(), nullable=True))
    op.add_column('posts', sa.Column('title', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'title')
    op.drop_column('posts', 'Htitle')
    # ### end Alembic commands ###
