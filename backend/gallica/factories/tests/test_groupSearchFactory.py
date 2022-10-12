from gallica.factories.groupSearchFactory import GroupSearchFactory
import unittest
from unittest.mock import MagicMock


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
        self.testFactory.getSearch()
        self.testFactory.ticket.getGroupingIntervals.assert_called_once()


if __name__ == '__main__':
    unittest.main()
