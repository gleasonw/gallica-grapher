from dataclasses import dataclass
from gallicaGetter.parse.date import Date


@dataclass
class PeriodOccurrenceRecord:
    date: Date
    count: int
    term: str
    ticketID: str
    requestID: str

    def get_row(self):
        row = [
            self.date.getYear(),
            self.date.getMonth(),
            self.date.getDay(),
            self.term
        ]
        (self.ticketID is not None) and row.append(self.ticketID)
        (self.requestID is not None) and row.append(self.requestID)
        row.append(self.count)
        return tuple(row)

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
