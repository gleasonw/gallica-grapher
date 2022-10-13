from gallica.factories.groupSearchFactory import GroupSearchFactory
import unittest
from unittest.mock import MagicMock
from gallica.search import Search


class TestGroupSearchFactory(unittest.TestCase):

    def setUp(self) -> None:
        self.testFactory = GroupSearchFactory(
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
        test = self.testFactory.getSearch()
        self.assertIsInstance(test, Search)


if __name__ == '__main__':
    unittest.main()
