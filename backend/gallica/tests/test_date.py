from unittest import TestCase
from dateparse import DateParse


class TestDate(TestCase):

    def test_get_date(self):
        fullDate = DateParse("1800-04-02")
        anotherFullDate = DateParse("1800-04-02")
        yearMon = DateParse("1800-09")
        yearSingleDigitMon = DateParse("1888-1")
        year = DateParse("1912")
        nonsense = DateParse("12??")
        moreNonsense = DateParse("")
        self.assertEqual(
            fullDate.getDate(),
            ['1800', '04', '02']
        )
        self.assertEqual(
            anotherFullDate.getDate(),
            ['1800', '04', '02']
        )
        self.assertEqual(
            yearMon.getDate(),
            ['1800', '09', None]
        )
        self.assertEqual(
            yearSingleDigitMon.getDate(),
            ['1888', '1', None]
        )
        self.assertEqual(
            year.getDate(),
            ['1912', None, None]
        )
        self.assertEqual(
            nonsense.getDate(),
            [None, None, None]
        )
        self.assertEqual(
            moreNonsense.getDate(),
            [None, None, None]
        )