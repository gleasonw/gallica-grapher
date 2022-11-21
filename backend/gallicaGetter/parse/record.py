from typing import List, Tuple


class Record:

    def __init__(self, **kwargs):
        self.post_init(kwargs)

    def post_init(self, kwargs):
        pass


class VolumeOccurrenceRecord:

    def __init__(
            self,
            paperTitle,
            paperCode,
            url,
            date,
            term,
            ticketID,
            requestID
    ):
        self.url = url
        self.date = date
        self.paperTitle = paperTitle
        self.paperCode = paperCode
        self.term = term
        self.ticketID = ticketID
        self.requestID = requestID

    def get_date(self):
        return self.date

    def get_paper_code(self):
        return self.paperCode

    def get_volume_code(self):
        return self.url.split('/')[-1]

    def __repr__(self):
        return f'OccurrenceRecord({self.term}, {self.paperTitle}, {self.url}, {self.date})'

    def getRow(self):
        row = [
            self.url,
            self.date.getYear(),
            self.date.getMonth(),
            self.date.getDay(),
            self.term,
        ]
        self.ticketID and row.append(self.ticketID)
        self.requestID and row.append(self.requestID)
        row.append(self.paperCode)
        row.append(self.paperTitle)
        return tuple(row)

    def getDisplayRow(self):
        return (
            self.term,
            self.paperTitle,
            self.date.getYear(),
            self.date.getMonth(),
            self.date.getDay(),
            self.url
        )


class PeriodOccurrenceRecord:

    def __init__(self, date, count, ticketID, term, requestID):
        self.date = date
        self.count = count
        self.term = term
        self.ticketID = ticketID
        self.requestID = requestID

    def getRow(self):
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

    def getDisplayRow(self):
        return (
            self.term,
            self.date.getYear(),
            self.date.getMonth(),
            self.date.getDay(),
            self.count
        )

    def __repr__(self):
        return f'GroupedCountRecord({self.date}, {self.term}, {self.count})'


class PaperRecord:

    def __init__(self, code, title, url):
        self.code = code
        self.title = title
        self.url = url
        self.publishingYears = []

    def __repr__(self):
        return f'PaperRecord({self.code}, {self.title}, {self.url}, [{self.publishingYears[0]}-{self.publishingYears[-1]}])'

    def getRow(self):
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


class ContentRecord:

    def __init__(self, num_results, pages):
        self.num_results = num_results
        self.pages = pages

    def __repr__(self):
        return f"ContentRecord(num_results={self.num_results}, first page={self.pages[0]})"

    def get_pages(self) -> List[Tuple[str, str]]:
        return self.pages


class ArkRecord:

    def __init__(self, code, years):
        self.code = code
        self.years = years
