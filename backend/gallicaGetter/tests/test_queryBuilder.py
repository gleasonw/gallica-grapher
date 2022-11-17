from unittest import TestCase
from gallicaGetter.fetch.query import OccurrenceQuery
from gallicaGetter.build.queryBuilder import OccurrenceQueryBuilder
from gallicaGetter.build.queryBuilder import PaperQueryBuilder
from unittest.mock import MagicMock


class TestQueryBuilder(TestCase):

    def setUp(self) -> None:
        self.builders = [
            OccurrenceQueryBuilder(MagicMock()),
            PaperQueryBuilder(MagicMock())
        ]

    def test_index_queries_with_num_results(self):
        test_queries = [
            (
                OccurrenceQuery(
                    searchMetaData=MagicMock(),
                    startDate=1900,
                    endDate=1901,
                    term='test',
                    startIndex=0,
                    numRecords=1,
                    endpoint='test'
                ),
                '1205'
            ),
            (
                OccurrenceQuery(
                    searchMetaData=MagicMock(),
                    startDate=1900,
                    endDate=1905,
                    term='test',
                    startIndex=0,
                    numRecords=1,
                    endpoint='test'
                ),
                '1895'
            ),
        ]
        results= self.builders[0].index_queries_by_num_results(test_queries)
        self.assertEqual(len(results), 63)
        self.assertIsInstance(results[0], OccurrenceQuery)