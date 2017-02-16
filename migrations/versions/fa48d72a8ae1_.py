"""empty message

Revision ID: fa48d72a8ae1
Revises: 8680f5fa40b2
Create Date: 2017-02-16 11:49:08.303057

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa48d72a8ae1'
down_revision = '8680f5fa40b2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('follows',
    sa.Column('follower_id', sa.Integer(), nullable=False),
    sa.Column('followed_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('follower_id', 'followed_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('follows')
    # ### end Alembic commands ###
