"""empty message

Revision ID: bfb70c548f99
Revises: None
Create Date: 2016-07-19 23:07:59.452517

"""

# revision identifiers, used by Alembic.
revision = 'bfb70c548f99'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('title', sa.String(length=128), nullable=True))
    op.drop_index('category', table_name='posts')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index('category', 'posts', ['category'], unique=True)
    op.drop_column('posts', 'title')
    ### end Alembic commands ###