from unittest import TestCase
from date import Date


class TestDate(TestCase):
    def setUp(self) -> None:
        self.fullDate = Date("2020-01-01")
        self.yearDate = Date("2020")
        self.monthDate = Date("2020-01")

    def test_get_year(self):
        self.assertEqual(self.fullDate.getYear(), "2020")
        self.assertEqual(self.yearDate.getYear(), "2020")
        self.assertEqual(self.monthDate.getYear(), "2020")

    def test_get_month(self):
        self.assertEqual(self.fullDate.getMonth(), "01")
        self.assertEqual(self.yearDate.getMonth(), None)
        self.assertEqual(self.monthDate.getMonth(), "01")

    def test_get_day(self):
        self.assertEqual(self.fullDate.getDay(), "01")
        self.assertEqual(self.yearDate.getDay(), None)
        self.assertEqual(self.monthDate.getDay(), None)