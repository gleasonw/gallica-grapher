from lxml import etree

from record import Record


class RecordBatch:
    def __init__(self,
                 query,
                 session,
                 startRecord=1,
                 numRecords=50,
                 ):

        self.dateJournalIdentifierResults = []
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
        self.params['exactSearch'] = "false"
        self.fetchXMLRoot()
        numResults = int(self.xmlRoot.find("{http://www.loc.gov/zing/srw/}numberOfRecords").text)
        return numResults

    def getRecordBatch(self):
        self.fetchXMLRoot()
        self.parseRecordsFromXML()
        return self.dateJournalIdentifierResults

    def fetchXMLRoot(self):
        response = self.session.get("", params=self.params)
        self.xmlRoot = etree.fromstring(response.content)
        et = etree.ElementTree(self.xmlRoot)
        et.write('output.xml', pretty_print=True)

    def parseRecordsFromXML(self):
        for result in self.xmlRoot.iter("{http://www.loc.gov/zing/srw/}record"):
            record = Record(result)
            if self.recordIsValid(record):
                self.addRecord(record)
            else:
                print(record.getIdentifier())
                self.numPurgedResults += 1

    def recordIsValid(self, record):

        dateOfHit = record.getDate()
        paperOfHit = record.getPaper()
        identifierOfHit = record.getIdentifier()
        if dateOfHit and paperOfHit:
            return self.recordIsUnique(dateOfHit, identifierOfHit)
        else:
            return False

    def recordIsUnique(self, currentDate, currentPaper):
        if self.dateJournalIdentifierResults:
            if self.currentResultEqualsPrior(currentDate, currentPaper):
                return False
        return True

    # TODO: What if the duplicate is not directly before?
    def currentResultEqualsPrior(self, currentDate, currentPaper):
        priorDate = self.dateJournalIdentifierResults[-1]['date']
        priorPaper = self.dateJournalIdentifierResults[-1]['identifier']
        if currentDate == priorDate and currentPaper == priorPaper:
            return True
        else:
            return False

    def addRecord(self, record):
        date = record.getDate()
        identifier = record.getIdentifier()
        paper = record.getPaper()
        fullResult = {
            'date': date,
            'identifier': identifier,
            'journalCode': paper
        }
        self.dateJournalIdentifierResults.append(fullResult)

    def getNumberPurgedResults(self):
        return self.numPurgedResults
