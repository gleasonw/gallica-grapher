from typing import List, Optional
from dataclasses import dataclass
from gallicaGetter.fetch.occurrenceQuery import OccurrenceQuery


@dataclass(slots=True)
class SearchArgs:
    terms: List[str] | str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    codes: Optional[List[str] | str] = None
    grouping: str = 'year'
    query_cache: Optional[List[OccurrenceQuery]] = None
    generate: bool = False
    num_results: Optional[int] = None
    start_index: Optional[int] = 0
    num_workers: Optional[int] = 15
    link_term: Optional[str] = None
    link_distance: Optional[int] = None
    onUpdateProgress = None
