from dataclasses import dataclass
from pydantic import BaseModel
from typing import List, Literal, Optional, Tuple

from backend.date import Date


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
    data: List[Tuple[float, float]]
    name: str


class Ticket(BaseModel):
    term: str
    year: int
    end_year: int
    codes: Optional[List[str]] = None
    source: Literal["livres", "presse", "lemonde"] = "presse"
    link_term: Optional[str] = None


@dataclass(slots=True)
class PeriodRecord:
    _date: Date
    count: float
    term: str

    @property
    def year(self):
        return self._date.year

    @property
    def month(self):
        return self._date.month

    @property
    def day(self):
        return self._date.day
