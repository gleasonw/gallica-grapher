from search import OccurrenceSearchFulfillment
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
    fetcher = Fetch('http://gallica.bnf.fr/SRU')
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
        fetcher
    )


def buildPaperFulfillment():
    pass

