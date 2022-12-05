from typing import List, Optional
from dataclasses import dataclass


@dataclass
class QueryArgs(slots=True):
    terms: List[str] | str
    grouping: str
    endpoint_url: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    codes: Optional[List[str] | str] = None
    link_term: Optional[str] = None
    link_distance: Optional[int] = None
