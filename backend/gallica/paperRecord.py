class PaperRecord:

    def __init__(self, code, title, url):
        self.code = None
        self.title = None
        self.url = None
        self.publishingYears = []
        self.publishingRange = [None, None]
        self.continuousRange = False

