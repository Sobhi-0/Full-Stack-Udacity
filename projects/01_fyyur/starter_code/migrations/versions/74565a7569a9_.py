"""empty message

Revision ID: 74565a7569a9
Revises: 6eb92efc94ec
Create Date: 2023-06-12 00:16:17.731784

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74565a7569a9'
down_revision = '6eb92efc94ec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.add_column(sa.Column('seeking_venue', sa.Boolean(), nullable=True))
        batch_op.drop_column('seeking_talent')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.add_column(sa.Column('seeking_talent', sa.BOOLEAN(), autoincrement=False, nullable=True))
        batch_op.drop_column('seeking_venue')

    # ### end Alembic commands ###
