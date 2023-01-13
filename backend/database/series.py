from typing import List, Generator

from pydantic import BaseModel


class SeriesDataPoint(BaseModel):
    date: str
    count: float


class Series(BaseModel):
    request_id: int
    data: List[SeriesDataPoint]
    name: str
