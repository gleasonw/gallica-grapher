from unittest import TestCase
from gallicaGetter.buildqueries.buildPaperQueries import build_paper_queries_for_codes
from gallicaGetter.fetch.paperQuery import PaperQuery
from unittest.mock import MagicMock
from gallicaGetter.buildqueries.argToQueryTransformations import NUM_CODES_PER_BUNDLE


class Test(TestCase):
    def test_build_paper_queries_for_codes(self):
        result = build_paper_queries_for_codes(['test1', 'test2'], 'test', MagicMock())

        query = result[0]
        self.assertIsInstance(query, PaperQuery)
        self.assertEqual(len(result), 1)

    def test_build_paper_queries_for_bundle_plus_1(self):
        result = build_paper_queries_for_codes(['test' for i in range(NUM_CODES_PER_BUNDLE + 1)], 'test', MagicMock())

        query = result[0]
        self.assertIsInstance(query, PaperQuery)
        self.assertEqual(len(result), 2)

