from occurrenceFetchDriver import OccurrenceFetchDriver
from parseFactory import buildParser
from query import Query
from urlsforterm import UrlsForTerm
from recordsToDBTransaction import RecordsToDBTransaction
from fetch import fetchAllAndTrackProgress
from fetch import fetchAll


def buildOccurrenceFetchDriver(
        options,
        progressTracker,
        requestID,
        dbConnection
):
    parse = buildParser()
    return OccurrenceFetchDriver(
        options,
        parse,
        UrlsForTerm().buildUrls,
        Query,
        RecordsToDBTransaction(dbConnection, requestID).insertResults,
        fetchAll,
        fetchAllAndTrackProgress,
        progressTracker
    )


def buildPaperFetchDriver():
    pass

