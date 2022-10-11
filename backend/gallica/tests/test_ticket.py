from unittest import TestCase
from unittest.mock import MagicMock
from gallica.ticket import Ticket


class TestTicket(TestCase):

    def setUp(self) -> None:
        self.monthGroupedTicket = Ticket(
            key=1,
            terms=['test'],
            codes=None,
            dateRange=(1900, 1901),
            linkTerm=None,
            linkDistance=None,
            fetchType='month'
        )
        self.yearGroupedTicket = Ticket(
            key=1,
            terms=['test'],
            codes=None,
            dateRange=(1900, 1901),
            linkTerm=None,
            linkDistance=None,
            fetchType='year'
        )
        self.ticketWithCodes = Ticket(
            key=1,
            terms=['test'],
            codes=['test'],
            dateRange=(1900, 1901),
            linkTerm=None,
            linkDistance=None,
            fetchType='year'
        )

    def test_get_id(self):
        self.fail()

    def test_get_grouping_intervals(self):
        self.fail()

    def test_get_code_bundles(self):
        self.fail()
