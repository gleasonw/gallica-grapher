import math
from unittest import TestCase
from unittest.mock import MagicMock

from gallicaGetter.buildqueries.argToQueryTransformations import (
    index_queries_by_num_results,
    build_indexed_queries,
    bundle_codes,
    NUM_CODES_PER_BUNDLE,
)
from gallicaGetter.fetch.occurrenceQuery import OccurrenceQuery


class TestArgQueryTransformations(TestCase):
    def setUp(self):
        self.test_1 = OccurrenceQuery(
            start_date="1900",
            end_date="1901",
            term="test",
            start_index=0,
            num_records=1,
            endpoint_url="test",
            num_results=1205,
        )
        self.test_2 = OccurrenceQuery(
            start_date="1900",
            end_date="1905",
            term="test",
            start_index=0,
            num_records=1,
            endpoint_url="test",
            num_results=1895,
        )

    def test_index_queries_by_num_results(self):
        test_queries = [
            self.test_1,
            self.test_2,
        ]
        results = index_queries_by_num_results(test_queries)
        self.assertEqual(len(results), 63)
        self.assertIsInstance(results[0], OccurrenceQuery)

    def test_build_indexed_queries(self):
        results = build_indexed_queries(
            queries=[self.test_1, self.test_2],
            api=MagicMock(),
        )
        self.assertEqual(len(results), 0)

    def test_bundle_codes(self):
        test = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"]
        results = bundle_codes(test)
        self.assertEqual(len(results), math.ceil(len(test) / NUM_CODES_PER_BUNDLE))
