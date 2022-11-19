import threading
from appsearch.search import build_searches_for_tickets
from appsearch.searchprogressstats import initProgressStats

RECORD_LIMIT = 1000000
MAX_DB_SIZE = 10000000


def buildRequest(identifier, argsBundles, conn):
    return Request(
        identifier=identifier,
        argsBundles=argsBundles,
        statKeeper=initProgressStats,
        searchBuilder=build_searches_for_tickets,
        conn=conn
    )


class Request(threading.Thread):
    def __init__(self, identifier, argsBundles, statKeeper, searchBuilder, conn):
        self.numResultsDiscovered = 0
        self.numResultsRetrieved = 0
        self.state = 'RUNNING'
        self.requestID = identifier
        self.estimateNumRecords = 0
        self.argsBundles = argsBundles
        self.searches = None
        self.statBuilder = statKeeper
        self.searchBuilder = searchBuilder
        self.searchProgressStats = self.initProgressStats()
        self.conn = conn
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
        self.searches = self.searchBuilder(
            args_for_tickets=self.argsBundles,
            stateHooks=self,
            conn=self.conn
        )
        self.estimateNumRecords = sum(
            search.getNumRecordsToBeInserted(onNumRecordsFound=lambda search, numRecordsDiscovered:
                self.searchProgressStats[search.identifier].setNumRecordsToFetch(numRecordsDiscovered)
            )
            for search in self.searches
        )
        if self.estimateNumRecords == 0:
            self.state = 'NO_RECORDS'
        else:
            if self.numRecordsUnderLimit(self.estimateNumRecords):
                self.doEachSearch()
            else:
                self.state = 'TOO_MANY_RECORDS'

    def numRecordsUnderLimit(self, numRecords):
        dbSpaceRemainingWithBuffer = MAX_DB_SIZE - self.get_number_rows_in_db() - 10000
        return numRecords < min(dbSpaceRemainingWithBuffer, RECORD_LIMIT)

    def get_number_rows_in_db(self):
        with self.conn.cursor() as curs:
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
            key: self.statBuilder(
                ticketID=key,
                grouping=argsBundle['grouping']
            )
            for key, argsBundle in self.argsBundles.items()
        }
        return progressDict


if __name__ == '__main__':
    from database.connContext import build_db_conn

    with build_db_conn() as conn:
        request = buildRequest(
            identifier='56',
            argsBundles={
                '1': {
                    'terms': 'brazza',
                    'grouping': 'year',
                    'startDate': 1880,
                    'endDate': 1990,
                    'codes': ['cb32895690j']
                },
                '2': {
                    'terms': 'brazza',
                    'grouping': 'year',
                    'startDate': 1880,
                    'endDate': 1990,
                    'codes': ['cb34448033b']
                }
            },
            conn=conn
        )
        request.start()
        while not request.state == 'COMPLETED':
            print(request.getProgressStats())
            print(request.state)