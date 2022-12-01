from pydantic import BaseModel
from typing import List, Optional, Union


class QueryArgModel(BaseModel):
    endpoint_url: str
    terms: List[str] | str
    grouping: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    codes: Optional[List[str] | str] = None
    link_term: Optional[str] = None
    link_distance: Optional[int] = None
