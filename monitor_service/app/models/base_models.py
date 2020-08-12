from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StatsModel(BaseModel):
    service: str
    url: str
    status_code: int
