class PaperRecord:

    def __init__(self, code, title, url):
        self.code = code
        self.title = title
        self.url = url
        self.publishingYears = []

    def getRow(self):
        return (
            self.title,
            self.publishingYears[0],
            self.publishingYears[-1],
            self.isContinuous(),
            self.code
        )

    def isContinuous(self):
        if len(self.publishingYears) > 1:
            return int(self.publishingYears[-1]) - int(self.publishingYears[0]) + 1 == len(self.publishingYears)
        else:
            return True


