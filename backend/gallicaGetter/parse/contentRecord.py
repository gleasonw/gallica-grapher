from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class ContentRecord:
    num_results: int
    pages: List[Tuple[str, str]]

    def __repr__(self):
        return f"ContentRecord(num_results={self.num_results}, first page={self.pages[0]})"