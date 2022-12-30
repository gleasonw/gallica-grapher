from typing import List, Optional

from pydantic import BaseModel


class Ticket(BaseModel):
    id: int
    terms: List[str] | str
    start_date: str
    end_date: str
    codes: Optional[List[str] | str] = None
    grouping: str = 'year'
    num_results: Optional[int] = None
    start_index: Optional[int] = 0
    num_workers: Optional[int] = 15
    link_term: Optional[str] = None
    link_distance: Optional[int] = None
