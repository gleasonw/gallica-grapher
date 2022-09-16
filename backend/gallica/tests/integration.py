from ticket import Ticket
from requestFactory import RequestFactory
import time
import psutil


def runTests():
    oneTest = getSearchOneTermInOnePaperOverRange()
    testTicket = getSearchOneTermInTwoPapersOverRange()
    secondTest = getSearchTwoTermsInTwoPapersOverRange()

    try:
        doTest(oneTest)
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
        ['paris'],
        ['cb328066631'],
        '1840',
        '1930'
    )
    return testTicket


def getSearchOneTermInOnePaperOverRange():
    testTicket = Ticket(
        '1234',
        ['paris'],
        ['cb328066631'],
        '1900',
        '1930'
    )
    return testTicket


def getSearchOneTermInTwoPapersOverRange():
    testTicket = Ticket(
        '1234',
        ['brazza'],
        ['cb328066631', 'cb32895690j'],
        '1900',
        '1910'
    )
    return testTicket


def getSearchTwoTermsInTwoPapersOverRange():
    testTicket = Ticket(
        '1234',
        ['brazza', 'paris'],
        ['cb328066631', 'cb32895690j'],
        '1900',
        '1910'
    )
    return testTicket


if __name__ == '__main__':
    runTests()
