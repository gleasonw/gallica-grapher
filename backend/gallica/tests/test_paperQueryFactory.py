from query import ArkQueryForNewspaperYears
import unittest
from paperQueryFactory import PaperQueryFactory
from query import PaperQuery
from unittest.mock import MagicMock


class TestPaperQueryFactory(unittest.TestCase):

    def setUp(self):
        self.testQueryFactory = PaperQueryFactory(
            gallicaAPI=MagicMock(),
            parse=MagicMock()
        )

    def test_buildSRUQueriesForCodes(self):
        codes = [1,2,3,4,5,6,7,8,9,10,11]

        test = self.testQueryFactory.buildSRUQueriesForCodes(codes)

        self.assertEqual(len(test), 2)
        for result in test:
            self.assertIsInstance(result, PaperQuery)

    def test_buildSRUQueriesForAllRecords(self):
        self.testQueryFactory.indexer = MagicMock()
        self.testQueryFactory.buildSRUQueriesForAllRecords()

        self.testQueryFactory.indexer.getNumResultsForEachQuery.assert_called()
        self.testQueryFactory.indexer.makeIndexedQueries.assert_called()

    def test_buildArkQueriesForCodes(self):
        test = self.testQueryFactory.buildArkQueriesForCodes([1,2,3,4,5])

        self.assertEqual(len(test), 5)
        for result in test:
            self.assertIsInstance(result, ArkQueryForNewspaperYears)

if __name__ == '__main__':
    unittest.main()
