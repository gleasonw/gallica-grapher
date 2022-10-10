from gallica.dto.arkRecord import ArkRecord
import unittest
from gallica.factories.paperSearchFactory import ParseArkRecord
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
        for tesResult in testResultGenerator:
            self.assertIsInstance(tesResult, ArkRecord)


if __name__ == '__main__':
    unittest.main()
