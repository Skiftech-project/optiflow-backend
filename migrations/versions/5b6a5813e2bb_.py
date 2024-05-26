"""empty message

Revision ID: 5b6a5813e2bb
Revises: 5cf2a3e06035
Create Date: 2024-05-26 18:10:41.353977

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b6a5813e2bb'
down_revision = '5cf2a3e06035'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('saved_calculation_templates', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['title'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('saved_calculation_templates', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    # ### end Alembic commands ###