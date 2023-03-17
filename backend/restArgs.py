from typing import Literal, Optional, List
from pydantic import BaseModel


class RestArgs(BaseModel):
    terms: List[str]
    codes: Optional[List[str]]
    year: Optional[int] = 0
    month: Optional[int] = 0
    end_year: Optional[int] = 0
    end_month: Optional[int] = 0
    cursor: Optional[int] = 0
    limit: Optional[int] = 10
    link_term: Optional[str] = None
    link_distance: Optional[int] = 0
    source: Literal["book", "periodical", "all"] = "all"
    sort: Literal["date", "relevance"] = "relevance"
