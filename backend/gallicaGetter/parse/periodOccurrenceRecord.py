from dataclasses import dataclass
from gallicaGetter.parse.date import Date


@dataclass
class PeriodOccurrenceRecord(slots=True):
    date: Date
    count: int
    term: str

    def get_display_row(self):
        return (
            self.term,
            self.date.getYear(),
            self.date.getMonth(),
            self.date.getDay(),
            self.count
        )

    def __repr__(self):
        return f'GroupedCountRecord({self.date}, {self.term}, {self.count})'
