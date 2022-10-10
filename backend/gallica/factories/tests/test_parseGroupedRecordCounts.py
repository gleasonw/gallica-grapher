from gallica.factories.groupSearchFactory import ParseGroupedRecordCounts
import unittest
from unittest.mock import MagicMock


class TestParseGroupedRecordCounts(unittest.TestCase):

    def setUp(self) -> None:
        self.testParse = ParseGroupedRecordCounts(
          parser=MagicMock()
        )

    def test_parse(self):
        self.testParse.parse(xml='test')
        self.testParse.parser.numRecords.assert_called_once_with('test')


if __name__ == '__main__':
    unittest.main()
