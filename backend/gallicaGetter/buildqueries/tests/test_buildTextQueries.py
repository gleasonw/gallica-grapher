from unittest import TestCase
from gallicaGetter.buildqueries.buildTextQueries import build_text_queries_for_codes
from gallicaGetter.fetch.fullTextQuery import FullTextQuery


class Test(TestCase):
    def test_build_text_queries_for_codes(self):
        test = build_text_queries_for_codes("test", "test")
        self.assertEqual(len(test), 1)
        self.assertIsInstance(test[0], FullTextQuery)
