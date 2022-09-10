class PaperFetchDriver:

    def __init__(self, parse):
        pass

    def recordIsUnique(self, record):
        if self.batch:
            if self.currentResultEqualsPrior(record):
                return False
        return True

    def getNumResults(self):
        numResults = self.xmlRoot.find(
            "{http://www.loc.gov/zing/srw/}numberOfRecords")
        if numResults is not None:
            numResults = numResults.text
            numResults = int(numResults)
        return numResults