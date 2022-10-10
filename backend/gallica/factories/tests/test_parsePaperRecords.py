import unittest
from unittest.mock import MagicMock
from gallica.factories.paperSearchFactory import ParsePaperRecords
from gallica.dto.paperRecord import PaperRecord


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.testParse = ParsePaperRecords(
            parser=MagicMock()
        )

    def test_parseResponsesToRecords(self):
        responses = [
            MagicMock(),
            MagicMock(),
        ]
        self.testParse.parser.getRecordsFromXML.return_value = [
            'record1',
            'record2',
        ]

        test = self.testParse.parseResponsesToRecords(responses)

        for testResult in test:
            self.assertIsInstance(testResult, PaperRecord)




if __name__ == '__main__':
    unittest.main()
