"""empty message

Revision ID: 10149a4e8f0e
Revises: 35e03aa48c14
Create Date: 2017-02-10 10:44:38.525025

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10149a4e8f0e'
down_revision = '35e03aa48c14'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('roles', sa.Column('default', sa.Boolean(), nullable=True))
    op.add_column('roles', sa.Column('permissions', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_roles_default'), 'roles', ['default'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_roles_default'), table_name='roles')
    op.drop_column('roles', 'permissions')
    op.drop_column('roles', 'default')
    # ### end Alembic commands ###