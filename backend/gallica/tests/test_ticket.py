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
            codes=['test' * 15],
            dateRange=(1900, 1901),
            linkTerm=None,
            linkDistance=None,
            fetchType='year'
        )

    def test_get_id(self):
        self.assertEqual(self.monthGroupedTicket.getID(), 1)
        self.assertEqual(self.yearGroupedTicket.getID(), 1)
        self.assertEqual(self.ticketWithCodes.getID(), 1)

    def test_get_grouping_intervals(self):
        self.assertEqual(
            self.monthGroupedTicket.getGroupingIntervals(),
            [
                ('1900-01-01', '1900-01-31'),
                ('1900-02-01', '1900-02-31'),
                ('1900-03-01', '1900-03-31'),
                ('1900-04-01', '1900-04-31'),
                ('1900-05-01', '1900-05-31'),
                ('1900-06-01', '1900-06-31'),
                ('1900-07-01', '1900-07-31'),
                ('1900-08-01', '1900-08-31'),
                ('1900-09-01', '1900-09-31'),
                ('1900-10-01', '1900-10-31'),
                ('1900-11-01', '1900-11-31'),
                ('1900-12-01', '1900-12-31'),
                ('1901-01-01', '1901-01-31'),
                ('1901-02-01', '1901-02-31'),
                ('1901-03-01', '1901-03-31'),
                ('1901-04-01', '1901-04-31'),
                ('1901-05-01', '1901-05-31'),
                ('1901-06-01', '1901-06-31'),
                ('1901-07-01', '1901-07-31'),
                ('1901-08-01', '1901-08-31'),
                ('1901-09-01', '1901-09-31'),
                ('1901-10-01', '1901-10-31'),
                ('1901-11-01', '1901-11-31'),
                ('1901-12-01', '1901-12-31')
            ]
        )
        self.assertEqual(
            self.yearGroupedTicket.getGroupingIntervals(),
            set(zip(range(1900, 1902), range(1900, 1902)))
        )

    def test_get_code_bundles(self):
        self.assertEqual(self.monthGroupedTicket.getCodeBundles(), [])
        self.assertEqual(self.yearGroupedTicket.getCodeBundles(), [])
        self.assertEqual(
            len(self.ticketWithCodes.getCodeBundles()),
            ceil(len(self.ticketWithCodes.codes) / NUM_CODES_PER_BUNDLE)
            )
