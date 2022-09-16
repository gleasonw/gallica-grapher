from ticket import Ticket
from requestFactory import RequestFactory
import time


def runTests():
    testTicket = getSearchOneTermInTwoPapersOverRange()
    testRequestFactory = RequestFactory([testTicket], 'testRequest')
    testRequest = testRequestFactory.build()
    testRequest.start()
    while not testRequest.finished:
        time.sleep(1)


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


if __name__ == '__main__':
    runTests()
