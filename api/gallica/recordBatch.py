from lxml import etree
from record import Record
from record import PaperRecord


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
        self.startRecord = startRecord
        self.numPurgedResults = 0
        self.numRecords = numRecords
        self.session = session
        self.xmlRoot = None
        self.params = {
            "version": 1.2,
            "operation": "searchRetrieve",
            "query": self.query,
            "exactSearch": "true",
            "startRecord": self.startRecord,
            "maximumRecords": self.numRecords,
            "collapsing": "disabled"
        }

    def getNumResults(self):
        self.fetchXMLRoot()
        numResults = self.xmlRoot\
            .find("{http://www.loc.gov/zing/srw/}numberOfRecords").text
        numResults = int(numResults)
        return numResults

    def getRecordBatch(self):
        self.fetchXMLRoot()
        self.parseRecordsFromXML()
        return self.batch

    def fetchXMLRoot(self):
        response = self.session.get("", params=self.params)
        self.xmlRoot = etree.fromstring(response.content)

    def parseRecordsFromXML(self):
        for result in self.xmlRoot.iter("{http://www.loc.gov/zing/srw/}record"):
            record = Record(result)
            if self.recordIsValid(record):
                self.addRecordToBatch(record)
            else:
                self.numPurgedResults += 1

    def recordIsValid(self, record):
        dateOfHit = record.getDate()
        paperOfHit = record.getPaperCode()
        urlOfHit = record.getUrl()
        if dateOfHit and paperOfHit:
            return self.recordIsUnique(dateOfHit, urlOfHit)
        else:
            return False

    def recordIsUnique(self, currentDate, currentPaper):
        if self.batch:
            if self.currentResultEqualsPrior(currentDate, currentPaper):
                return False
        return True

    # TODO: What if the duplicate is not directly before?
    def currentResultEqualsPrior(self, currentDate, currentPaper):
        priorDate = self.batch[-1]['date']
        priorPaper = self.batch[-1]['url']
        if currentDate == priorDate and currentPaper == priorPaper:
            return True
        else:
            return False

    def addRecordToBatch(self, record):
        date = record.getDate()
        url = record.getUrl()
        paper = record.getPaperCode()
        fullResult = {
            'date': date,
            'url': url,
            'paperCode': paper
        }
        self.batch.append(fullResult)

    def getNumberPurgedResults(self):
        return self.numPurgedResults


class PaperRecordBatch(RecordBatch):

    def __init__(self,
                 query,
                 session,
                 startRecord=1,
                 numRecords=50):

        super().__init__(query,
                         session,
                         startRecord,
                         numRecords)

    def parseRecordsFromXML(self):
        for result in self.xmlRoot.iter("{http://www.loc.gov/zing/srw/}record"):
            record = PaperRecord(result)
            if self.recordIsValid(record):
                self.addRecordToBatch(record)
            else:
                self.numPurgedResults += 1

    def recordIsValid(self, record):
        code = record.getPaperCode()
        if code:
            return True
        else:
            return False

    def addRecordToBatch(self, record):
        date = record.getDate()
        code = record.getPaperCode()
        title = record.getTitle()
        fullResult = {
            'date': date,
            'code': code,
            'title': title
        }
        self.batch.append(fullResult)
