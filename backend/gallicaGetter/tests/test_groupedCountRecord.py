from unittest.mock import MagicMock
import unittest
from groupedCountRecord import GroupedCountRecord


class TestGroupedCountRecord(unittest.TestCase):

    def setUp(self) -> None:
        self.testRecord = GroupedCountRecord(
            date=MagicMock(
                getYear=MagicMock(return_value=2020),
                getMonth=MagicMock(return_value=1),
                getDay=MagicMock(return_value=1)
            ),
            count=1,
            term='test',
            ticketID='testticketid',
            requestID='testrequestid'
        )

    def test_getRow(self):
        row = self.testRecord.getRow()
        self.assertEqual(
            row,
            (2020, 1, 1, 'test', 'testticketid', 'testrequestid', 1)
        )


if __name__ == '__main__':
    unittest.main()
