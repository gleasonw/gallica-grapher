import re

from lxml import etree

from GettingAndGraphing.result import Result


class ResultBatch:
    def __init__(self, query, startRecord, numRecords, session):
        self.dateJournalIdentifierResults = []
        self.query = query
        self.queryHitNumber = 0
        self.startRecord = startRecord
        self.numPurgedResults = 0
        self.numRecords = numRecords
        self.session = session
        self.hitData = None

    def establishTotalHits(self, query, collapseResults):
        if collapseResults:
            collapseSetting = "true"
        else:
            collapseSetting = "disabled"
        parameters = {
            "version": 1.2,
            "operation": "searchRetrieve",
            "collapsing": collapseSetting,
            "exactSearch": "false",
            "query": query,
            "startRecord": 0,
            "maximumRecords": 1
        }
        response = self.session.get("", params=parameters)
        root = etree.fromstring(response.content)
        numResults = int(root[2].text)
        return numResults

    def getResultBatch(self):
        parameters = {
            "version": 1.2,
            "operation": "searchRetrieve",
            "query": self.query,
            "exactSearch": "true",
            "startRecord": self.startRecord,
            "maximumRecords": self.numRecords,
            "collapsing": "disabled"
        }
        response = self.session.get("", params=parameters)
        root = etree.fromstring(response.content)
        self.getResultsFromXML(root)

    def getResultsFromXML(self, xml):
        for hit in xml.iter("{http://www.loc.gov/zing/srw/}record"):
            if hit:
                result = Result(hit)
                dateOfHit = result.getDate()
                paperOfHit = result.getPaper()
                identifierOfHit = result.getIdentifier()
                if dateOfHit and paperOfHit:
                    if self.resultIsUnique(dateOfHit, identifierOfHit):
                        self.addResultToFinalList(result)
                else:
                    self.numPurgedResults += 1
            else:
                self.numPurgedResults += 1

    def resultIsUnique(self, currentDate, currentPaper):
        if self.dateJournalIdentifierResults:
            return self.currentResultEqualsPrior(currentDate, currentPaper)
        else:
            return True

    def currentResultEqualsPrior(self, currentDate, currentPaper):
        priorDate = self.dateJournalIdentifierResults[-1]['date']
        priorPaper = self.dateJournalIdentifierResults[-1]['identifier']
        if currentDate == priorDate and currentPaper == priorPaper:
            self.numPurgedResults = self.numPurgedResults + 1
            return False
        else:
            return True

    def addResultToFinalList(self, result):
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

    def getResultList(self):
        return self.dateJournalIdentifierResults
