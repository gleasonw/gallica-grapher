from searchlauncher import OccurrenceSearchFulfillment
from parseFactory import buildParser
from query import Query
from urlsforticket import UrlsForTicket
from recordsToDBTransaction import RecordsToDBTransaction
from fetch import Fetch #MAKE FACTORY


def buildOccurrenceFulfillment(
        options,
        requestID,
        ticketID,
        dbConnection
):
    parse = buildParser()
    insertResults = RecordsToDBTransaction(
        requestID=requestID,
        ticketID=ticketID,
        conn=dbConnection,
        getPaperRecordsForMissingCodes=None
    ).insertResults
    return OccurrenceSearchFulfillment(
        options,
        parse,
        UrlsForTicket().buildUrls,
        Query,
        insertResults,
        fetchAll,
        fetchAllAndTrackProgress,
    )


def buildPaperFulfillment():
    pass

