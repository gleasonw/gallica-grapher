from unittest import TestCase
from gallicaGetter.query import OccurrenceQuery
from gallicaGetter.queryBuilder import OccurrenceQueryBuilder
from gallicaGetter.queryBuilder import PaperQueryBuilder
from unittest.mock import MagicMock


class TestQueryBuilder(TestCase):

    def setUp(self) -> None:
        self.builders = [
            OccurrenceQueryBuilder(MagicMock()),
            PaperQueryBuilder(MagicMock())
        ]

    def test_responds_to_make_query(self):
        [self.assertTrue(hasattr(builder, 'makeQuery')) for builder in self.builders]

    def test_index_queries_with_num_results(self):
        testQueries = [
            (
                OccurrenceQuery(
                    searchMetaData=MagicMock(),
                    startDate=1900,
                    endDate=1901,
                    term='test',
                    startIndex=0,
                    numRecords=1,
                ),
                1205
            ),
            (
                OccurrenceQuery(
                    searchMetaData=MagicMock(),
                    startDate=1900,
                    endDate=1905,
                    term='test',
                    startIndex=0,
                    numRecords=1,
                ),
                1895
            ),
        ]
        results= self.builders[0].indexQueriesWithNumResults(testQueries)
        self.assertEqual(len(results), 63)
        self.assertIsInstance(results[0], OccurrenceQuery)