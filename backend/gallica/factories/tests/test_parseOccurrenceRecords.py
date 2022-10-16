from gallica.dto.occurrenceRecord import OccurrenceRecord
import unittest
from parseOccurrenceRecords import ParseOccurrenceRecords
from unittest.mock import MagicMock


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.testParse = ParseOccurrenceRecords(
            parser=MagicMock(),
            requestID=1,
            ticketID=1
        )

    def test_parseResponsesToRecords(self):
        testResponses = [
            MagicMock(),
            MagicMock(),
        ]
        self.testParse.parser.return_value = ['test1', 'test2']
        testResults = self.testParse.parseResponsesToRecords(testResponses)
        for result in testResults:
            self.assertIsInstance(result, OccurrenceRecord)

if __name__ == '__main__':
    unittest.main()
