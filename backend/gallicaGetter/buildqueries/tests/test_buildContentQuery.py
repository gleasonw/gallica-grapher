from unittest import TestCase
from gallicaGetter.buildqueries.buildContentQuery import build_query_for_ark_and_term
from gallicaGetter.fetch.query import ContentQuery


class Test(TestCase):
    def test_build_query_for_ark_and_term(self):
        result = build_query_for_ark_and_term('test', 'test', 'test')
        self.assertIsInstance(result, ContentQuery)

