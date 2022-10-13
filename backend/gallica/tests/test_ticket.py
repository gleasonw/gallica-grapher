from unittest import TestCase
from math import ceil
from gallica.ticket import Ticket
from gallica.ticket import NUM_CODES_PER_BUNDLE


class TestTicket(TestCase):

    def setUp(self) -> None:
        self.monthGroupedTicket = Ticket(
            key=1,
            terms=['test'],
            codes=None,
            dateRange=(1900, 1901),
            linkTerm=None,
            linkDistance=None,
            searchType='month'
        )
        self.yearGroupedTicket = Ticket(
            key=1,
            terms=['test'],
            codes=None,
            dateRange=(1900, 1901),
            linkTerm=None,
            linkDistance=None,
            searchType='year'
        )
        self.ticketWithCodes = Ticket(
            key=1,
            terms=['test'],
            codes=['test' * 15],
            dateRange=(1900, 1901),
            linkTerm=None,
            linkDistance=None,
            searchType='year'
        )

    def test_get_id(self):
        self.assertEqual(self.monthGroupedTicket.getID(), 1)
        self.assertEqual(self.yearGroupedTicket.getID(), 1)
        self.assertEqual(self.ticketWithCodes.getID(), 1)

    def test_get_month_grouping_intervals(self):
        monthGroups = self.monthGroupedTicket.getGroupingIntervals()
        self.assertTrue(('1900-01-01', '1900-02-01') in monthGroups)
        self.assertTrue(('1900-12-01', '1901-01-01') in monthGroups)
        self.assertTrue(('1901-12-01', '1902-01-01') in monthGroups)

    def test_get_year_grouping_intervals(self):
        yearGroups = self.yearGroupedTicket.getGroupingIntervals()
        self.assertTrue(('1900-01-01', '1901-01-01') in yearGroups)
        self.assertTrue(('1901-01-01', '1902-01-01') in yearGroups)

    def test_get_code_bundles(self):
        self.assertEqual(self.monthGroupedTicket.getCodeBundles(), [])
        self.assertEqual(self.yearGroupedTicket.getCodeBundles(), [])
        self.assertEqual(
            len(self.ticketWithCodes.getCodeBundles()),
            ceil(len(self.ticketWithCodes.codes) / NUM_CODES_PER_BUNDLE)
            )
