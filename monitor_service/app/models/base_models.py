from pydantic import BaseModel


class StatsModel(BaseModel):
    service: str
    url: str
    status_code: int
    response_time: float
    request_timestamp: float
