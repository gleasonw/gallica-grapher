import re

from lxml import etree

from GettingAndGraphing.result import Result


class ResultBatch:
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
        self.hitData = None
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
        response = self.session.get("", params=parameters)
        root = etree.fromstring(response.content)
        numResults = int(root[2].text)
        return numResults

    def getResultBatch(self):
        response = self.session.get("", params=self.params)
        root = etree.fromstring(response.content)
        self.getResultsFromXML(root)
        return self.dateJournalIdentifierResults

    def getResultsFromXML(self, xml):
        for result in xml.iter("{http://www.loc.gov/zing/srw/}record"):
            if self.resultIsValid(result):
                self.addResult(result)
            else:
                self.numPurgedResults += 1

    def resultIsValid(self, hit):
        result = Result(hit)
        dateOfHit = result.getDate()
        paperOfHit = result.getPaper()
        identifierOfHit = result.getIdentifier()
        if dateOfHit and paperOfHit:
            return self.resultIsUnique(dateOfHit, identifierOfHit)
        else:
            return False

    def resultIsUnique(self, currentDate, currentPaper):
        if self.dateJournalIdentifierResults:
            return self.checkIfCurrentResultEqualsPrior(currentDate, currentPaper)
        else:
            return True

    # TODO: What if the duplicate is not directly before?
    def checkIfCurrentResultEqualsPrior(self, currentDate, currentPaper):
        priorDate = self.dateJournalIdentifierResults[-1]['date']
        priorPaper = self.dateJournalIdentifierResults[-1]['identifier']
        if currentDate == priorDate and currentPaper == priorPaper:
            self.numPurgedResults = self.numPurgedResults + 1
            return False
        else:
            return True

    def addResult(self, result):
        date = result.getDate
        identifier = result.getIdentifier()
        paper = result.getPaper()
        fullResult = {
            'date': date,
            'identifier': identifier,
            'journalCode': paper
        }
        self.dateJournalIdentifierResults.append(fullResult)

    def getNumberPurgedResults(self):
        return self.numPurgedResults
