import unittest
from unittest.mock import MagicMock
from queryIndexer import QueryIndexer


class TestQueryIndexer(unittest.TestCase):

    def setUp(self) -> None:
        self.testIndexer = QueryIndexer(
            gallicaAPI=MagicMock(),
            parse=MagicMock(),
            makeQuery=MagicMock()
        )

    def test_getNumResultsForEachQuery(self):
        queries = [MagicMock(), MagicMock()]
        self.testIndexer.gallicaAPI.fetchAll.return_value = [
            MagicMock(
                query=queries[0],
                xml=MagicMock()
            ),
            MagicMock(
                query=queries[1],
                xml=MagicMock()
            )
        ]
        self.testIndexer.parse.getNumRecords.return_value = 100

        result = self.testIndexer.getNumResultsForEachQuery(queries)

        self.assertDictEqual(result, {queries[0]: 100, queries[1]: 100})

    def test_makeIndexedQueries(self):
        baseQueries = {
            MagicMock(): 100,
            MagicMock(): 200
        }
        self.testIndexer.makeQuery.return_value = "testQuery"

        result = self.testIndexer.makeIndexedQueries(baseQueries)

        self.assertEqual(result, ["testQuery"] * 6)


if __name__ == '__main__':
    unittest.main()
