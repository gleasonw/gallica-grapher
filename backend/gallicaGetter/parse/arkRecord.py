from dataclasses import dataclass
from typing import List


@dataclass
class ArkRecord:
    code: str
    years: List[int]

