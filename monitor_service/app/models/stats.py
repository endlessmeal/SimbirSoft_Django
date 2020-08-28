from . import db
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Stats(db.Model):
    __tablename__ = "stats"

    UUID = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    service = db.Column("service", db.String, nullable=False)
    url = db.Column("url", db.String, nullable=False)
    status_code = db.Column("status_code", db.Integer)
    response_time = db.Column("response_time", db.Float)
    request_timestamp = db.Column("request_timestamp", db.Float)
