from typing import List, Tuple

from pydantic import BaseModel


class Series(BaseModel):
    request_id: int
    data: List[Tuple[int, float]]
    name: str
