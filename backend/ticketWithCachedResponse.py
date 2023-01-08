from dataclasses import dataclass
from typing import List, Optional

from gallicaGetter.fetch.occurrenceQuery import OccurrenceQuery


@dataclass(frozen=True, slots=True)
class TicketWithCachedResponse:
    id: int
    terms: List[str] | str
    start_date: int
    end_date: int
    cached_response: List[OccurrenceQuery]
    codes: Optional[List[str] | str] = None
    grouping: str = "year"
    num_results: Optional[int] = None
    start_index: Optional[int] = 0
    num_workers: Optional[int] = 15
    link_term: Optional[str] = None
    link_distance: Optional[int] = None
