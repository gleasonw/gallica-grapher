from unittest import TestCase
from math import ceil
from gallica.params import Params
from gallica.params import NUM_CODES_PER_BUNDLE


class TestParams(TestCase):

    def setUp(self) -> None:
        self.monthGroupedParams = Params(
            key=1,
            terms=['test'],
            codes=None,
            startDate='1900',
            endDate='1901',
            linkTerm=None,
            linkDistance=None,
            grouping='month',
        )
        self.yearGroupedParams = Params(
            key=1,
            terms=['test'],
            codes=None,
            startDate='1900',
            endDate='1901',
            linkTerm=None,
            linkDistance=None,
            grouping='year'
        )
        self.ticketWithCodes = Params(
            key=1,
            terms=['test'],
            codes=['test' * 15],
            startDate='1900',
            endDate='1901',
            linkTerm=None,
            linkDistance=None,
            grouping='year'
        )

    def test_get_month_grouping_intervals(self):
        monthGroups = self.monthGroupedParams.getDateGroupings()
        self.assertTrue(('1900-01-02', '1900-02-01') in monthGroups)
        self.assertTrue(('1900-12-02', '1901-01-01') in monthGroups)
        self.assertTrue(('1901-12-02', '1902-01-01') in monthGroups)

    def test_get_year_grouping_intervals(self):
        yearGroups = self.yearGroupedParams.getDateGroupings()
        self.assertTrue(('1900-01-01', '1901-01-01') in yearGroups)
        self.assertTrue(('1901-01-01', '1902-01-01') in yearGroups)

    def test_get_code_bundles(self):
        self.assertEqual(self.monthGroupedParams.getCodeBundles(), [])
        self.assertEqual(self.yearGroupedParams.getCodeBundles(), [])
        self.assertEqual(
            len(self.ticketWithCodes.getCodeBundles()),
            ceil(len(self.ticketWithCodes.codes) / NUM_CODES_PER_BUNDLE)
            )
