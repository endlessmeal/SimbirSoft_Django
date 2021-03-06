from messages.app.models import db
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Template(db.Model):
    __tablename__ = "templates"

    UUID = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = db.Column("name", db.String, nullable=False)
    text = db.Column("text", db.String, nullable=False)
    created_at = db.Column(
        "created_at", db.DateTime, nullable=False, server_default=db.func.now()
    )
