"""empty message

Revision ID: 71f004b817b9
Revises: 8392615472eb
Create Date: 2024-05-08 15:00:59.559812

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '71f004b817b9'
down_revision = '8392615472eb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('token_block_list', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.String(), nullable=True))
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('token_block_list', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###
