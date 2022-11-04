from unittest import TestCase
from gallicaGetter.dateGrouping import DateGrouping


class TestDateGrouping(TestCase):

    def test_get_month_grouping_intervals(self):
        monthGroups = DateGrouping('1900-01-01', '1902-01-01', 'month')
        self.assertTrue(('1900-01-02', '1900-02-01') in monthGroups)
        self.assertTrue(('1900-12-02', '1901-01-01') in monthGroups)
        self.assertTrue(('1901-12-02', '1902-01-01') in monthGroups)

    def test_get_year_grouping_intervals(self):
        yearGroups = DateGrouping('1900-01-01', '1902-01-01', 'year')
        self.assertTrue(('1900-01-01', '1901-01-01') in yearGroups)
        self.assertTrue(('1901-01-01', '1902-01-01') in yearGroups)