from unittest import TestCase
from unittest.mock import MagicMock, call
from queryIndexer import QueryIndexer


class TestQueryIndexer(TestCase):

    def setUp(self) -> None:
        self.testIndexer = QueryIndexer()
        self.testIndexer.fetch = MagicMock()
        self.testIndexer.parse = MagicMock()
        self.testIndexer.makeQuery = MagicMock()

        self.testIndexer.productionBuildIndexQueries = self.testIndexer.buildIndexQueries
        self.testIndexer.productionMakeQueriesWithIndices = self.testIndexer.makeQueriesWithIndices
        self.testIndexer.productionGetNumResults = self.testIndexer.getNumResults

        self.testIndexer.buildIndexQueries = MagicMock()
        self.testIndexer.makeQueriesWithIndices = MagicMock()
        self.testIndexer.getNumResults = MagicMock()

    def test_build_index_queries(self):
        cql = ['cql1', 'cql2']
        self.testIndexer.makeQueriesWithIndices.side_effect = lambda x: (x for x in [x])

        result = self.testIndexer.productionBuildIndexQueries(cql)

        results = [list(result) for result in result]

        self.assertListEqual(
            results,
            [['cql1'], ['cql2']]
        )

    def test_make_queries_with_indices(self):
        query = 'test url'
        self.testIndexer.getNumResults.return_value = 100

        result = self.testIndexer.productionMakeQueriesWithIndices(query)

        result = list(result)

        self.assertEqual(len(result), 2)
        self.testIndexer.makeQuery.assert_called_with(
            url=query,
            startIndex=51,
            numRecords=50,
            collapsing=False
        )

    def test_get_num_results(self):
        cql = 'test cql string'
        self.testIndexer.fetch.fetchAll.return_value = MagicMock(
            responseXML='test response xml'
        )
        self.testIndexer.parse.numRecords.return_value = 100

        result = self.testIndexer.productionGetNumResults(cql)

        self.testIndexer.fetch.fetchAll.assert_called_with(
            [self.testIndexer.makeQuery.return_value]
        )
        self.testIndexer.parse.numRecords.assert_called_with(
            'test response xml'
        )
        self.assertEqual(result, 100)
