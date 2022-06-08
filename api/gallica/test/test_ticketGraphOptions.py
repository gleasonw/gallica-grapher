from unittest import TestCase
from gallica.ticketGraphOptions import TicketGraphOptions


class TestTicketGraphOptions(TestCase):
    options = TicketGraphOptions(
        ['1234', '4321'],
        groupby='year'
    )
    print(options.getOptions())
