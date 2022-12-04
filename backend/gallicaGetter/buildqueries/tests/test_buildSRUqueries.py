from unittest import TestCase
from gallicaGetter.buildqueries.buildSRUqueries import (
    build_base_queries,
    build_base_queries_at_indices
)
from unittest.mock import MagicMock
from gallicaGetter.fetch.occurrenceQuery import OccurrenceQuery
from gallicaGetter.queryArgs import QueryArgs


class Test(TestCase):
    def setUp(self) -> None:
        self.month_args = QueryArgs(
            terms='test',
            codes='test',
            start_date='1980',
            end_date='1985',
            grouping='month',
            endpoint_url='test',
        )
        self.year_args = QueryArgs(
            terms='test',
            codes='test',
            start_date='1980',
            end_date='1985',
            grouping='year',
            endpoint_url='test',
        )
        self.all_args = QueryArgs(
            terms='test',
            codes='test',
            startDate='1980',
            endDate='1985',
            grouping='all',
            endpoint_url='test',
        )
        self.api = MagicMock(get=lambda x: [
            MagicMock(query=i, data='test')
            for i in x
        ])
        self.query_cache = 'test'

    def test_build_queries(self):
        test = build_base_queries(self.month_args)
        self.assertEqual(len(test), 72)

        test = build_base_queries(self.year_args)
        self.assertEqual(len(test), 6)

        test = build_base_queries(self.all_args)
        self.assertEqual(len(test), 1)

    def test_build_base_queries_at_indices(self):
        test = build_base_queries(self.month_args)
        indexed_test = build_base_queries_at_indices(test, 0)

        self.assertEqual(len(list(indexed_test)), 72)
        for query in indexed_test:
            self.assertEqual(query.start_index, 0)
            self.assertEqual(query.num_records, 1)
            self.assertIsInstance(query, OccurrenceQuery)
