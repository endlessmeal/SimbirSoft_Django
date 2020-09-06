import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base(metadata=sa.MetaData())


class TableUser(Base):
    __tablename__ = "users"
    UUID = sa.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    username = sa.Column("username", sa.String, unique=True, nullable=False)
    password = sa.Column("password", sa.String, nullable=False)
    name = sa.Column("name", sa.String, nullable=False)
    age = sa.Column("age", sa.Integer, nullable=False)
    created_at = sa.Column(
        "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
    )
    updated_at = sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        server_onupdate=sa.func.now(),
    )
