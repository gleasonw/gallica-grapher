from SearchFactory import SearchFactory
import unittest
from unittest.mock import MagicMock
from gallica.getandput import GetAndPut


class TestGroupSearchFactory(unittest.TestCase):

    def setUp(self) -> None:
        self.testFactory = SearchFactory(
            ticket=MagicMock(),
            onUpdateProgress=MagicMock(),
            dbLink=MagicMock(),
            parse=MagicMock(),
            requestID=MagicMock(),
            sruFetcher=MagicMock(),
            onAddingResultsToDB=MagicMock(),
            queryBuilder=MagicMock()
        )

    def test_getSearch(self):
        self.assertIsInstance(self.testFactory.prepare(MagicMock()), GetAndPut)


if __name__ == '__main__':
    unittest.main()
