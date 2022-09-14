from unittest import TestCase
from batchedQueries import BatchedQueries


class TestBatchedQueries(TestCase):

    def setUp(self) -> None:
        self.testBatcher = BatchedQueries(batchSize=2)

    def test_batchQueries(self):
        queries = ['query1', 'query2', 'query3', 'query4', 'query5']

        result = self.testBatcher.batchQueries(queries)

        self.assertListEqual(
            result,
            [['query1', 'query2'], ['query3', 'query4'], ['query5']]
        )


