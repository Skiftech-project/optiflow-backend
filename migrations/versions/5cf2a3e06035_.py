"""empty message

Revision ID: 5cf2a3e06035
Revises: b9ca0f9f66d8
Create Date: 2024-05-22 00:02:12.364507

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '5cf2a3e06035'
down_revision = 'b9ca0f9f66d8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('saved_calculation_templates', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title', sa.String(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('saved_calculation_templates', schema=None) as batch_op:
        batch_op.drop_column('title')

    # ### end Alembic commands ###
