from ticket import Ticket
from gallica.search import Search
from fulfillerFactory import buildOccurrenceFulfillment



def buildTicket(
        options,
        ticketID,
        requestID,
        dbConnection,
        progressThread
):
    driver = Search()
    fulfiller = buildOccurrenceFulfillment(
        options,
        requestID,
        ticketID,
        dbConnection
    )
    return Ticket(
        ticketID,
        requestID,
        driver,
        fulfiller,
        progressThread
    )
