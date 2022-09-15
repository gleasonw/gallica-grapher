from ticket import Ticket
from requestFactory import RequestFactory
import time


if __name__ == '__main__':
    testTicket = Ticket(
        '1234',
        ['paris'],
        ['cb328066631', 'cb32895690j'],
        '1900',
        '1930'
    )
    testRequestFactory = RequestFactory([testTicket], 'testRequest')
    testRequest = testRequestFactory.build()
    testRequest.start()
    while not testRequest.finished:
        time.sleep(1)
