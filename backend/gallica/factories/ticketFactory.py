from ticket import Ticket
from gallica.searchlauncher import SearchLauncher
from fulfillmentFactory import buildOccurrenceFulfillment



def buildTicket(
        options,
        ticketID,
        requestID,
        dbConnection
):
    driver = SearchLauncher()
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
        fulfiller
    )
