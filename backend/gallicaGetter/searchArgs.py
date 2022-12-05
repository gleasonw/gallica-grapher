from typing import List, Optional
from dataclasses import dataclass


@dataclass
class SearchArgs(slots=True):
    terms: List[str] | str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    codes: Optional[List[str] | str] = None
    grouping: str = 'year'
    generate: bool = False
    num_results: Optional[int] = None
    start_index: Optional[int] = 0
    num_workers: Optional[int] = 15
    link_term: Optional[str] = None
    link_distance: Optional[int] = None
    onUpdateProgress = None
    query_cache = None
