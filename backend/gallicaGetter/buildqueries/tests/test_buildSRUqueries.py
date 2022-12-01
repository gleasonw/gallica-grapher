from unittest import TestCase
from gallicaGetter.buildqueries.buildSRUqueries import (
    build_base_queries,
    build_base_queries_at_indices
)
from unittest.mock import MagicMock
from gallicaGetter.fetch.OccurrenceQuery import OccurrenceQuery


class Test(TestCase):
    def setUp(self) -> None:
        self.month_args = {
            'terms': 'test',
            'codes': 'test',
            'startDate': '1980',
            'endDate': '1985',
            'grouping': 'month',
        }
        self.year_args = {
            'terms': 'test',
            'codes': 'test',
            'startDate': '1980',
            'endDate': '1985',
            'grouping': 'year',
        }
        self.all_args = {
            'terms': 'test',
            'codes': 'test',
            'startDate': '1980',
            'endDate': '1985',
            'grouping': 'all',
        }
        self.endpoint_url = 'test'
        self.api = MagicMock(get=lambda x: [
            MagicMock(query=i, data='test')
            for i in x
        ])
        self.query_cache = 'test'

    def test_build_queries(self):
        test = build_base_queries(self.month_args, endpoint_url=self.endpoint_url)
        self.assertEqual(len(test), 72)

        test = build_base_queries(self.year_args, endpoint_url=self.endpoint_url)
        self.assertEqual(len(test), 6)

        test = build_base_queries(self.all_args, endpoint_url=self.endpoint_url)
        self.assertEqual(len(test), 1)

    def test_build_base_queries_at_indices(self):
        test = build_base_queries(self.month_args, endpoint_url=self.endpoint_url)
        indexed_test = build_base_queries_at_indices(test, 0, endpoint_url=self.endpoint_url)

        self.assertEqual(len(list(indexed_test)), 72)
        for query in indexed_test:
            self.assertEqual(query.startIndex, 0)
            self.assertEqual(query.numRecords, 1)
            self.assertIsInstance(query, OccurrenceQuery)
