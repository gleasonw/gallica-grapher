import unittest
from unittest.mock import MagicMock
from occurrenceRecord import OccurrenceRecord


class TestOccurrenceRecord(unittest.TestCase):

    def setUp(self) -> None:
        self.testRecord = OccurrenceRecord(
            paperTitle='testTitle',
            paperCode='testCode',
            url='testUrl',
            date=MagicMock(
                getYear=MagicMock(return_value='testYear'),
                getMonth=MagicMock(return_value='testMonth'),
                getDay=MagicMock(return_value='testDay')
            ),
            term='testTerm',
            ticketID='testTicketID',
            requestID='testRequestID'
        )

    def test_getRow(self):
        row = self.testRecord.getRow()

        self.assertEqual(
            row,
            (
                'testUrl',
                'testYear',
                'testMonth',
                'testDay',
                'testTerm',
                'testTicketID',
                'testRequestID',
                'testCode',
                'testTitle'
            )
        )

if __name__ == '__main__':
    unittest.main()
