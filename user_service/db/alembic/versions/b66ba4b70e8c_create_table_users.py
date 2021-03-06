"""create table users

Revision ID: b66ba4b70e8c
Revises: 
Create Date: 2020-07-21 20:39:36.581906

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "b66ba4b70e8c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("UUID", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String, unique=True, nullable=False),
        sa.Column("password", sa.String, nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("age", sa.Integer, nullable=False),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
            server_onupdate=sa.func.now(),
        ),
    )


def downgrade():
    op.drop_table("users")
