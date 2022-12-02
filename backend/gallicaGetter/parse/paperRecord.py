from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PaperRecord:
    code: str
    title: str
    url: str
    publishingYears: Optional[List[int]] = None

    def __repr__(self):
        return f'PaperRecord({self.code}, {self.title}, {self.url}, [{self.publishingYears[0]}-{self.publishingYears[-1]}])'

    def get_row(self):
        if self.publishingYears:
            startDate = self.publishingYears[0]
            endDate = self.publishingYears[-1]
        else:
            startDate = None
            endDate = None
        return (
            self.title,
            startDate,
            endDate,
            self.isContinuous(),
            self.code
        )

    def addYearsFromArk(self, years):
        self.publishingYears = years

    def isContinuous(self):
        if self.publishingYears:
            return int(self.publishingYears[-1]) - int(self.publishingYears[0]) + 1 == len(self.publishingYears)
        else:
            return False
