from gallica.search import Search
from allSearchFactory import AllSearchFactory
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
        )

    def test_getSearch(self):
        self.assertIsInstance(self.testFactory.prepare(MagicMock()), Search)
