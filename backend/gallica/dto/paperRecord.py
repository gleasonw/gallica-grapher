class PaperRecord:

    def __init__(self, code, title, url):
        self.code = code
        self.title = title
        self.url = url
        self.publishingYears = []
        self.continuousRange = False

    def getRow(self):
        return (
            self.title,
            self.code,
            self.publishingYears[0],
            self.publishingYears[-1],
            self.continuousRange
        )


