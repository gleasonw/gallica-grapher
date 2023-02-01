from typing import List, Literal, Optional, Tuple
from pydantic import BaseModel

from gallicaGetter.fetch.occurrenceQuery import OccurrenceQuery


class Ticket(BaseModel):
    terms: List[str]
    start_date: int
    end_date: int
    codes: Optional[List[str]] = None
    grouping: Literal["month", "year", "all"] = "year"
    id: Optional[int] = None
    backend_source: Literal["gallica", "pyllica"] = "pyllica"
    cached_response: Optional[List[OccurrenceQuery]] = None
    link: Optional[Tuple[str, int]] = None
    source: Optional[Literal["book", "periodical", "all"]] = "all"
