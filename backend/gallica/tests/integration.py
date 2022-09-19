from ticket import Ticket
from requestFactory import RequestFactory
import time
import psutil
from papersearchrunner import PaperSearchRunner
from parseFactory import buildParser
from concurrentfetch import ConcurrentFetch
from schemaLinkForSearch import SchemaLinkForSearch
from utils.psqlconn import PSQLconn
from paperQueryFactory import PaperQueryFactory


def runTests():

    ticket = getSearchOneTermInAllPapersOverRange()

    try:
        doTest(ticket)
    except Exception as e:
        print("Test failure.")
        raise


def doTest(ticket):
    testRequestFactory = RequestFactory([ticket], 'testRequest')
    testRequest = testRequestFactory.build()
    testRequest.start()
    while not testRequest.finished:
        print(psutil.Process().memory_info().rss / 1024 / 1024)
        print(testRequest.ticketProgressStats)
        time.sleep(1)


def getSearchOneTermInOnePaperOverRange():
    testTicket = Ticket(
        '1234',
        ['brazza'],
        ['cb32895690j'],
        '1863,1944'
    )
    return testTicket


def getSearchOneTermInTwoPapersOverRange():
    testTicket = Ticket(
        '1234',
        ['brazza'],
        ['cb328066631', 'cb32895690j'],
        '1900'
    )
    return testTicket


def getSearchTwoTermsInTwoPapersOverRange():
    testTicket = Ticket(
        '1234',
        ['brazza', 'paris'],
        ['cb328066631', 'cb32895690j'],
        '1900,1930'
    )
    return testTicket


def getSearchOneTermInAllPapersOverRange():
    testTicket = Ticket(
        '1234',
        ['brazza'],
        [],
        ['1850','1950']
    )
    return testTicket


def getAllPapers():
    parse = buildParser()
    sruFetcher = ConcurrentFetch('https://gallica.bnf.fr/SRU')
    dbLink = SchemaLinkForSearch(
        requestID='',
        conn=PSQLconn().getConn()
    )
    paperSearch = PaperSearchRunner(
        parse=parse,
        paperQueryFactory=PaperQueryFactory(),
        sruFetch=sruFetcher,
        arkFetch=ConcurrentFetch('https://gallica.bnf.fr/services/Issues'),
        insert=dbLink.insertRecordsIntoPapers
    )
    paperSearch.addAllFetchableRecordsToDB()



if __name__ == '__main__':
    runTests()
