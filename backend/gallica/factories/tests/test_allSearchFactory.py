from gallica.search import Search
from gallica.factories.allSearchFactory import AllSearchFactory
from unittest import TestCase
from unittest.mock import MagicMock


class TestAllSearchFactory(TestCase):

    def setUp(self) -> None:
        self.testFactory = AllSearchFactory(
            ticket=MagicMock(),
            dbLink=MagicMock(),
            requestID=MagicMock(),
            parse=MagicMock(),
            onUpdateProgress=MagicMock(),
            sruFetcher=MagicMock(),
            queryBuilder=MagicMock(),
            onAddingResultsToDB=MagicMock(),
            onAddingMissingPapersToDB=MagicMock()
        )

    def test_getSearch(self):
        self.testFactory.getSearch()
        self.assertIsInstance(self.testFactory.getSearch(), Search)
