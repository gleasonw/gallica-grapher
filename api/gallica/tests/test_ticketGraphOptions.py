from unittest import TestCase
from gallica.ticketGraphSeriesBatch import TicketGraphSeriesBatch


class TestTicketGraphOptions(TestCase):
    options = TicketGraphSeriesBatch(
        '4321',
        groupby='year',
    )
    print(options.getSeries())
