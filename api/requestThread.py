import threading
from ticketQuery import TicketQuery

# for testing
import uuid


class RequestThread(threading.Thread):
    def __init__(self,
                 searchTerms,
                 papers,
                 yearRange,
                 requestID,
                 eliminateEdgePapers=False):
        self.keywords = searchTerms
        self.papers = papers
        self.yearRange = yearRange
        self.tolerateEdgePapers = eliminateEdgePapers
        self.progress = 0
        self.currentTerm = ""
        self.graphJSONForTicket = None
        self.numResultsDiscovered = 0
        self.numResultsRetrieved = 0
        self.topPapersForTerms = []
        self.id = requestID
        super().__init__()

    def run(self):
        requestToRun = TicketQuery(

            self.keywords,
            self.papers,
            self.yearRange,
            self.tolerateEdgePapers,
            self)
        requestToRun.run()

    def setProgress(self, amount):
        self.progress = amount

    def getProgress(self):
        return self.progress

    def setCurrentTerm(self, term):
        self.currentTerm = term

    def getCurrentTerm(self):
        return self.currentTerm

    def setNumDiscovered(self, total):
        self.numResultsDiscovered = total

    def getNumDiscovered(self):
        return self.numResultsDiscovered

    def setNumRetrieved(self, count):
        self.numResultsRetrieved = count

    def getNumRetrieved(self):
        return self.numResultsRetrieved

    def getRequestID(self):
        return self.id

    def setTopPapers(self, papers):
        self.topPapersForTerms = papers

    def getTopPapers(self):
        return self.topPapersForTerms

    def setGraphJSON(self, json):
        self.graphJSONForTicket = json

    def getGraphJSON(self):
        return self.graphJSONForTicket


if __name__ == "__main__":
    request = RequestThread(["brazza"],
                            [],
                            [1901, 1904],
                            str(uuid.uuid4()),
                            eliminateEdgePapers=False)
    request.run()
