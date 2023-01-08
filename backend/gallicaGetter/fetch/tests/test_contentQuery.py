from unittest import TestCase

from gallicaGetter.fetch.contentQuery import ContentQuery


class TestOCRQuery(TestCase):
    def setUp(self) -> None:
        self.ocrQuery = ContentQuery(ark="test", term="test", endpoint_url="test")

    def test_get_fetch_params(self):
        test = self.ocrQuery.get_params_for_fetch()

        self.assertDictEqual(test, {"ark": "test", "query": "test"})
