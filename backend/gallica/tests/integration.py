from ticket import Ticket
from requestFactory import RequestFactory
import time
import psutil
from papersearchrunner import PaperSearchRunner
from parseFactory import buildParser
from fetch import Fetch
from tableLink import TableLink
from utils.psqlconn import PSQLconn
from paperQueryFactory import PaperQueryFactory


def runTests():
    try:
        getAllPapers()
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
        '1900'
    )
    return testTicket


def getSearchOneTermInAllPapersOverRange():
    testTicket = Ticket(
        '1234',
        ['brazza'],
        [],
        '1900'
    )
    return testTicket


def getAllPapers():
    parse = buildParser()
    sruFetcher = Fetch('https://gallica.bnf.fr/SRU')
    dbLink = TableLink(
        requestID='',
        conn=PSQLconn().getConn()
    )
    paperSearch = PaperSearchRunner(
        parse=parse,
        paperQueryFactory=PaperQueryFactory(),
        sruFetch=sruFetcher,
        arkFetch=Fetch('https://gallica.bnf.fr/services/Issues'),
        insert=dbLink.insertRecordsIntoPapers
    )
    paperSearch.addAllFetchableRecordsToDB()



if __name__ == '__main__':
    runTests()
