import unittest
from unittest.mock import MagicMock
from gallicaGetter.parse.volumeOccurrenceRecord import VolumeOccurrenceRecord


class TestOccurrenceRecord(unittest.TestCase):

    def setUp(self) -> None:
        self.testRecord = VolumeOccurrenceRecord(
            paper_title='testTitle',
            paper_code='testCode',
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
        row = self.testRecord.get_row()

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
