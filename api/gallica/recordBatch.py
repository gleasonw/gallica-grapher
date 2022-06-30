from lxml import etree
from gallica.record import KeywordRecord
from gallica.record import PaperRecord
from gallica.gallicaSession import GallicaSession


class RecordBatch:
    def __init__(self,
                 query,
                 session,
                 startRecord=1,
                 numRecords=50,
                 ):
        self.batch = []
        self.query = query
        self.queryHitNumber = 0
        self.numPurgedResults = 0
        self.session = session
        self.xmlRoot = None
        self.params = {
            "version": 1.2,
            "operation": "searchRetrieve",
            "query": self.query,
            "exactSearch": "False",
            "startRecord": startRecord,
            "maximumRecords": numRecords,
            "collapsing": "disabled"
        }

    def getNumberPurgedResults(self):
        return self.numPurgedResults

    def getNumResults(self):
        self.fetchXML()
        numResults = self.xmlRoot.find(
            "{http://www.loc.gov/zing/srw/}numberOfRecords").text
        numResults = int(numResults)
        return numResults

    def getRecordBatch(self):
        self.fetchXML()
        self.parseRecordsFromXML()
        return self.batch

    # TODO: Investigate requests toolbelt threading module
    # TODO: Move to a new class focused solely on concurrent requests
    def fetchXML(self):
        response = self.session.get(
            "",
            params=self.params,
            timeout=15)
        self.xmlRoot = etree.fromstring(response.content)

    def parseRecordsFromXML(self):
        pass


class KeywordRecordBatch(RecordBatch):

    def __init__(self,
                 query,
                 session,
                 startRecord=1,
                 numRecords=50):
        super().__init__(
            query,
            session,
            startRecord=startRecord,
            numRecords=numRecords
        )

    def parseRecordsFromXML(self):
        for result in self.xmlRoot.iter("{http://www.loc.gov/zing/srw/}record"):
            record = KeywordRecord(result)
            if record.isValid() and self.recordIsUnique(record):
                self.batch.append(record)
            else:
                self.numPurgedResults += 1

    def recordIsUnique(self, record):
        if self.batch:
            if self.currentResultEqualsPrior(record):
                return False
        return True

    # TODO: What if the duplicate is not directly before?
    def currentResultEqualsPrior(self, record):
        priorRecord = self.batch[-1]
        if record.getDate() == priorRecord.getDate() and record.getPaperCode() == priorRecord.getPaperCode():
            return True
        else:
            return False


class PaperRecordBatch(RecordBatch):

    def __init__(
            self,
            query,
            session,
            startRecord=1,
            numRecords=50):

        super().__init__(
            query,
            session,
            startRecord=startRecord,
            numRecords=numRecords)

        self.params["collapsing"] = "true"

    # TODO: at the end of bulk queries, run date queries for each code, so leave date unset here. One session = better, and we can better employ concurrency (get more batches of date information per request?).
    def parseRecordsFromXML(self):
        gallicaSessionForPaperYears = GallicaSession(
            "https://gallica.bnf.fr/services/Issues").getSession()
        for result in self.xmlRoot.iter(
                "{http://www.loc.gov/zing/srw/}record"):
            record = PaperRecord(
                result,
                gallicaSessionForPaperYears)
            if record.isValid():
                self.batch.append(record)
            else:
                self.numPurgedResults += 1

