from lxml import etree
from .record import KeywordRecord
from .record import PaperRecord
from requests_toolbelt import sessions
from .timeoutAndRetryHTTPAdapter import TimeoutAndRetryHTTPAdapter


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
        numResults = self.xmlRoot \
            .find("{http://www.loc.gov/zing/srw/}numberOfRecords").text
        numResults = int(numResults)
        return numResults

    def getRecordBatch(self):
        self.fetchXML()
        self.parseRecordsFromXML()
        return self.batch

    # TODO: Investigate requests toolbelt threading module
    def fetchXML(self):
        response = self.session.get("",
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

    def parseRecordsFromXML(self):
        gallicaSessionForPaperYears = sessions.BaseUrlSession(
            "https://gallica.bnf.fr/services/Issues"
        )
        adapter = TimeoutAndRetryHTTPAdapter()
        gallicaSessionForPaperYears.mount("https://", adapter)
        for result in self.xmlRoot.iter("{http://www.loc.gov/zing/srw/}record"):
            record = PaperRecord(result, gallicaSessionForPaperYears)
            if record.isValid():
                self.batch.append(record)
            else:
                self.numPurgedResults += 1

