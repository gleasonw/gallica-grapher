from unittest import TestCase
from gallicaGetter.fetch.query import OccurrenceQuery
from gallicaGetter.buildqueries.argToQueryTransformations import (
    index_queries_by_num_results,
    build_indexed_queries,
    bundle_codes,
    NUM_CODES_PER_BUNDLE
)
from unittest.mock import MagicMock
import math


class TestArgQueryTransformations(TestCase):

    def setUp(self):
        self.test_1 = OccurrenceQuery(
            searchMetaData=MagicMock(),
            startDate=1900,
            endDate=1901,
            term='test',
            startIndex=0,
            numRecords=1,
            endpoint='test'
        )
        self.test_2 = OccurrenceQuery(
            searchMetaData=MagicMock(),
            startDate=1900,
            endDate=1905,
            term='test',
            startIndex=0,
            numRecords=1,
            endpoint='test'
        )

    def test_index_queries_by_num_results(self):
        test_queries = [
            (self.test_1, 1205),
            (self.test_2, 1895)
        ]
        results = index_queries_by_num_results(test_queries, endpoint_url='nonsense')
        self.assertEqual(len(results), 63)
        self.assertIsInstance(results[0], OccurrenceQuery)

    def test_build_indexed_queries(self):
        results = build_indexed_queries(
            queries=[self.test_1, self.test_2],
            api=MagicMock(),
            endpoint_url='nonsense'
        )
        self.assertEqual(len(results), 0)

    def test_bundle_codes(self):
        test = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']
        results = bundle_codes(test)
        self.assertEqual(len(results), math.ceil(len(test)/NUM_CODES_PER_BUNDLE))


