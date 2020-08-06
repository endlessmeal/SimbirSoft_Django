"""added templates table

Revision ID: 99d9eb454d03
Revises: 
Create Date: 2020-08-06 21:45:51.752471

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

import uuid

# revision identifiers, used by Alembic.
revision = '99d9eb454d03'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'templates',
        sa.Column(str(UUID(as_uuid=True)), sa.String, primary_key=True, default=uuid.uuid4, unique=True, nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('text', sa.String, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('templates')
