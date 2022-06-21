from math import ceil

from .keywordQuery import KeywordQueryAllPapers
from .keywordQuery import KeywordQuerySelectPapers


class RequestTicket:

    def __init__(self,
                 ticket,
                 key,
                 progresstrack,
                 dbconnection,
                 session):

        self.keywords = ticket["terms"]
        self.papersAndCodes = ticket["papersAndCodes"]
        self.yearRange = ticket["dateRange"]
        self.ticketID = key
        self.progressThread = progresstrack
        self.connectionToDB = dbconnection
        self.session = session
        self.keywordQueries = []
        self.topPapers = []
        self.totalResults = 0
        self.numBatchesRetrieved = 0
        self.numBatches = 0

# TODO: Get rid of top paper sending, add "finished adding to database" check?
    def run(self):
        if self.papersAndCodes:
            self.initQueryObjects(self.genSelectPaperQuery)
        else:
            self.initQueryObjects(self.genAllPaperQuery)
        self.sumResultsOfEachTicket()
        self.startQueries()

    def initQueryObjects(self, generator):
        for keyword in self.keywords:
            keywordQuery = generator(keyword)
            self.keywordQueries.append(keywordQuery)

    def genSelectPaperQuery(self, keyword):
        query = KeywordQuerySelectPapers(
            keyword,
            self.papersAndCodes,
            self.yearRange,
            self.ticketID,
            self.updateProgress,
            self.connectionToDB,
            self.session)
        return query

    def genAllPaperQuery(self, keyword):
        query = KeywordQueryAllPapers(
            keyword,
            self.yearRange,
            self.ticketID,
            self.updateProgress,
            self.connectionToDB,
            self.session)
        return query

    def sumResultsOfEachTicket(self):
        for query in self.keywordQueries:
            numResultsForKeyword = query.getEstimateNumResults()
            self.totalResults += numResultsForKeyword

    def startQueries(self):
        self.numBatches = ceil(self.totalResults / 50)
        for query in self.keywordQueries:
            query.runSearch()

    def updateProgress(self):
        self.numBatchesRetrieved += 1
        progressPercent = self.numBatchesRetrieved/self.numBatches
        progressPercent *= 100
        progressPercent = int(progressPercent)
        self.progressThread.setProgress(progressPercent)
