from pydantic import BaseModel
from typing import List, Literal, Optional, Tuple


class Progress(BaseModel):
    num_results_discovered: int
    num_requests_to_send: int
    num_requests_sent: int
    estimate_seconds_to_completion: int
    random_paper: str
    random_text: str
    state: Literal[
        "too_many_records",
        "completed",
        "error",
        "no_records",
        "running",
        "adding_missing_papers",
    ]
    backend_source: Literal["gallica", "pyllica"]


class Series(BaseModel):
    request_id: int
    data: List[Tuple[float, float]]
    name: str


class Ticket(BaseModel):
    terms: List[str]
    start_date: int
    end_date: int
    codes: Optional[List[str]] = None
    grouping: Literal["month", "year", "all"] = "year"
    backend_source: Literal["gallica", "pyllica"] = "pyllica"
    link: Optional[Tuple[str, int]] = None
    source: Optional[Literal["book", "periodical", "all"]] = "all"
