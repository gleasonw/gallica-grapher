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




