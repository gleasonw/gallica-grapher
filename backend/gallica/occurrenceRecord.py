
class OccurrenceRecord:

    def __init__(self, paperCode, url, date):
        self.url = url
        self.date = date
        self.paperCode = paperCode
        self.keyword = None
        self.ticketID = None
        dateText = f'{date.year}-{date.month}-{date.day}'
        self.uniquenessCheck = f'{self.paperCode}{dateText}'

