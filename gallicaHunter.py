import re

import requests
from lxml import etree


class GallicaHunter:

    def __init__(self, query, isYearRange, recordNumber, startRecord):
        self.dateJournalIdentifierResults = []
        self.isYearRange = isYearRange
        self.query = query
        self.queryHitNumber = 0
        self.reachEndOfResults = False
        self.recordNumber = recordNumber
        self.startRecord = startRecord

    def huntSomePapers(self):
        pass

    def hunt(self):
        parameters = {"version": 1.2, "operation": "searchRetrieve", "collapsing": "false", "query": self.query,
                      "startRecord": self.startRecord, "maximumRecords": 50}
        response = requests.get("https://gallica.bnf.fr/SRU", params=parameters)
        success = False
        while not success:
            try:
                root = etree.fromstring(response.content)
                success = True
            except etree.XMLSyntaxError as e:
                print("\n\n ****Gallica spat at you!**** \n")
                print(response.url)

        self.hitListCreator(root)

    def hitListCreator(self, targetXMLroot):
        for queryHit in targetXMLroot.iter("{http://www.loc.gov/zing/srw/}record"):
            self.queryHitNumber = self.queryHitNumber + 1
            data = queryHit[2][0]
            dateOfHit = data.find('{http://purl.org/dc/elements/1.1/}date').text
            dateOfHit = self.standardizeSingleDate(dateOfHit)
            journalOfHit = data.find('{http://purl.org/dc/elements/1.1/}title').text
            journalOfHit = re.sub(',', '', journalOfHit)
            identifierOfHit = data.find('{http://purl.org/dc/elements/1.1/}identifier').text
            fullResult = [dateOfHit, journalOfHit, identifierOfHit]
            self.dateJournalIdentifierResults.append(fullResult)

    def getResultList(self):
        return self.dateJournalIdentifierResults

    def standardizeSingleDate(self, dateToStandardize):
        lengthOfDate = len(dateToStandardize)
        if lengthOfDate != 10:
            if lengthOfDate == 4:
                return (dateToStandardize + "-01-01")
            elif lengthOfDate == 7:
                return (dateToStandardize + "-01")
            elif lengthOfDate == 9:
                dates = dateToStandardize.split("-")
                lowerDate = int(dates[0])
                higherDate = int(dates[1])
                newDate = (lowerDate + higherDate) // 2
                return (str(newDate) + "-01-01")
        else:
            return (dateToStandardize)

    def establishTotalHits(self):
        counterToEnsureSuccess = 1
        for j in range(counterToEnsureSuccess):
            parameters = dict(version=1.2, operation="searchRetrieve", collapsing="true", exactSearch="false",
                              query=self.query, startRecord=0, maximumRecords=1)
            response = requests.get("https://gallica.bnf.fr/SRU", params=parameters)
            try:
                root = etree.fromstring(response.content)
            except etree.XMLSyntaxError as e:
                print("\n\n ****Gallica spat at you!**** \n")
                print(response.url)
                counterToEnsureSuccess = counterToEnsureSuccess + 1
                continue
        return int(root[2].text)

    def progressReporter(self):
        progress = str(((self.queryHitNumber / self.totalHits) * 100))
        return progress

