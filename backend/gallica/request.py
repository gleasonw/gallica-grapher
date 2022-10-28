import threading
from utils.psqlconn import PSQLconn
from gallica.search import buildSearch
from gallica.searchprogressstats import initProgressStats
import time
import psutil

RECORD_LIMIT = 1000000
MAX_DB_SIZE = 10000000


def buildRequest(identifier, argsBundles):
    return Request(
        identifier=identifier,
        argsBundles=argsBundles,
        statKeeper=initProgressStats,
        searchBuilder=buildSearch
    )


class Request(threading.Thread):
    def __init__(self, identifier, argsBundles, statKeeper, searchBuilder):
        self.numResultsDiscovered = 0
        self.numResultsRetrieved = 0
        self.state = 'RUNNING'
        self.requestID = identifier
        self.estimateNumRecords = 0
        self.dbConn = PSQLconn().getConn()
        self.argsBundles = argsBundles
        #TODO: Why not build searches here? Likewise for progress stats?
        self.searches = None
        self.searchProgressStats = self.initProgressStats()
        super().__init__()

    def getProgressStats(self):
        return {
            key: self.searchProgressStats[key].get()
            for key in self.argsBundles.keys()
        }

    def setSearchState(self, ticketID, state):
        self.searchProgressStats[ticketID].setState(state)

    def onSearchChangeToAll(self, ticketID):
        self.searchProgressStats[ticketID].setGrouping('all')

    def setSearchProgressStats(self, progressStats):
        ticketID = progressStats['ticketID']
        self.searchProgressStats[ticketID].update(progressStats)

    def run(self):
        self.searches = gallica.search.build(
            argBundles=self.argsBundles,
            stateHooks=self
        )
        numRecords = sum(
            search.getNumRecordsToBeInserted(
                onNumRecordsFound=lambda search, numRecordsDiscovered:
                    self.searchProgressStats[search.identifier].setNumRecordsToFetch(numRecordsDiscovered)
            )
            for search in self.searches
        )
        if numRecords == 0:
            self.state = 'NO_RECORDS'
        else:
            if self.numRecordsUnderLimit(numRecords):
                self.doEachSearch()
            else:
                self.state = 'TOO_MANY_RECORDS'

    def numRecordsUnderLimit(self, numRecords):
        dbSpaceRemainingWithBuffer = MAX_DB_SIZE - self.getNumberRowsStoredInAllTables() - 10000
        return numRecords < min(dbSpaceRemainingWithBuffer, RECORD_LIMIT)

    def getNumberRowsStoredInAllTables(self):
        with self.dbConn.cursor() as curs:
            curs.execute(
                """
                SELECT sum(reltuples)::bigint AS estimate
                FROM pg_class
                WHERE relname IN ('results', 'papers');
                """
            )
            return curs.fetchone()[0]

    def doEachSearch(self):
        for search in self.searches:
            self.state = 'RUNNING'
            search.getRecordsFromAPIAndInsertToDB()
            self.setSearchState(
                ticketID=search.identifier,
                state='COMPLETED'
            )
        self.state = 'COMPLETED'

    def initProgressStats(self):
        progressDict = {
            key: initProgressStats(
                ticketID=key,
                grouping=argsBundle['grouping']
            )
            for key, argsBundle in self.argsBundles.items()
        }
        return progressDict


if __name__ == '__main__':
    argsBundles ={
        0: {
            'terms': ['paix'],
            'codes': [],
            'startDate': 1870,
            'endDate': 1885,
            'linkTerm': None,
            'linkDistance': 10,
            'grouping': 'month'
        }
    }
    testRequest = Request(
        argsBundles=argsBundles,
        requestID='45'
    )
    testRequest.start()
    while testRequest.state != "COMPLETED":
        time.sleep(1)
        #print memory usage in mb
        print(psutil.Process().memory_info().rss / 1000000)
        print(testRequest.getProgressStats())
