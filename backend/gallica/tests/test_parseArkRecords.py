from gallica.dto.arkRecord import ArkRecord
import unittest
from parseArkRecord import ParseArkRecord
from unittest.mock import MagicMock


class TestParseArkRecord(unittest.TestCase):

    def setUp(self) -> None:
        self.testParse = ParseArkRecord(
            parser=MagicMock(),
        )

    def test_parseResponsesToRecords(self):
        testResultGenerator = self.testParse.parseResponsesToRecords(
            [
                MagicMock(),
                MagicMock(),
            ]
        )
        for testResult in testResultGenerator:
            self.assertIsInstance(testResult, ArkRecord)


if __name__ == '__main__':
    unittest.main()
