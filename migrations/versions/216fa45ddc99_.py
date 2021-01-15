"""empty message

Revision ID: 216fa45ddc99
Revises: 
Create Date: 2021-01-14 16:37:29.953196

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '216fa45ddc99'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('plane',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ident_public_key', sa.String(), nullable=True),
    sa.Column('ident_private_key', sa.String(), nullable=True),
    sa.Column('current_latitude', sa.Float(), nullable=True),
    sa.Column('current_longitude', sa.Float(), nullable=True),
    sa.Column('current_compass', sa.Integer(), nullable=True),
    sa.Column('current_altitude', sa.Integer(), nullable=True),
    sa.Column('last_update', sa.DateTime(), nullable=True),
    sa.Column('ever_received_data', sa.Boolean(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('atc_id', sa.String(), nullable=True),
    sa.Column('description_of_location', sa.String(), nullable=True),
    sa.Column('full_plane_description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('plane')
    # ### end Alembic commands ###