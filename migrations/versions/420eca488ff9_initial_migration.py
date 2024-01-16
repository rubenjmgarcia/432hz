"""Initial migration

Revision ID: 420eca488ff9
Revises: 
Create Date: 2024-01-11 13:58:10.118580

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '420eca488ff9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('photo', sa.String(length=255), nullable=True))
        batch_op.alter_column('role',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(length=20),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('role',
               existing_type=sa.String(length=20),
               type_=sa.VARCHAR(length=128),
               nullable=False)
        batch_op.drop_column('photo')

    # ### end Alembic commands ###