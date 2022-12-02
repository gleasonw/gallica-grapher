from dataclasses import dataclass
from gallicaGetter.parse.date import Date


@dataclass
class VolumeOccurrenceRecord:
    paper_title: str
    paper_code: str
    url: str
    date: Date
    term: str
    ticketID: str
    requestID: str

    def get_volume_code(self):
        return self.url.split('/')[-1]

    def __repr__(self):
        return f'OccurrenceRecord({self.term}, {self.paper_title}, {self.url}, {self.date})'

    def get_row(self):
        row = [
            self.url,
            self.date.getYear(),
            self.date.getMonth(),
            self.date.getDay(),
            self.term,
        ]
        self.ticketID and row.append(self.ticketID)
        self.requestID and row.append(self.requestID)
        row.append(self.paper_code)
        row.append(self.paper_title)
        return tuple(row)

    def get_display_row(self):
        return (
            self.term,
            self.paper_title,
            self.date.getYear(),
            self.date.getMonth(),
            self.date.getDay(),
            self.url
        )
