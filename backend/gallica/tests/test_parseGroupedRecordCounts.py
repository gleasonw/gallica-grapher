from gallica.dto.groupedCountRecord import GroupedCountRecord
from groupSearchFactory import ParseGroupedRecordCounts
import unittest
from unittest.mock import MagicMock


class TestParseGroupedRecordCounts(unittest.TestCase):

    def setUp(self) -> None:
        self.testParse = ParseGroupedRecordCounts(
            parser=MagicMock(),
            ticketID='test',
            requestID='test'
        )

    def test_parse(self):
        test = self.testParse.parseResponsesToRecords(
            [
                MagicMock(),
                MagicMock(),
            ]
        )
        for testResult in test:
            self.assertIsInstance(testResult, GroupedCountRecord)


if __name__ == '__main__':
    unittest.main()
