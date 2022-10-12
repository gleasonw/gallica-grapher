from requestFactory import RequestFactory
import time
import psutil


def runTests():
    ticket = getSearchOneTermInOnePaperOverRange()

    try:
        doTest(ticket)
    except Exception as e:
        print("Test failure.")
        raise


def doTest(ticket):
    testRequestFactory = RequestFactory(ticket, '45')
    testRequest = testRequestFactory.buildRequest()
    testRequest.start()
    while testRequest.state != 'COMPLETED':
        print(psutil.Process().memory_info().rss / 1024 / 1024)
        print(testRequest.getProgressStats())
        time.sleep(1)


def getSearchOneTermInOnePaperOverRange():
    testTicket = {
        0: {
            'terms': ['brazza'],
            'codes': [],
            'dateRange': [1882, 1883],
            'linkTerm': None,
            'linkDistance': None,
            'fetchType' : 'all'
        }
    }
    return testTicket


if __name__ == '__main__':
    runTests()