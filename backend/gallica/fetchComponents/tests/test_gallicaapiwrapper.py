from unittest.mock import MagicMock
from unittest import TestCase
from gallica.fetchComponents.gallicaResponseWrapper import GallicaResponseWrapper
from gallica.fetchComponents.gallicaapiwrapper import GallicaAPIWrapper


class TestGallicaAPIWrapper(TestCase):

    def setUp(self) -> None:
        self.gallicaAPIWrapper = GallicaAPIWrapper(baseUrl="https://gallica.bnf.fr/SRU")

    def test_get(self):
        self.gallicaAPIWrapper.http = MagicMock()
        response = self.gallicaAPIWrapper.get(query=MagicMock(
            getFetchParams=MagicMock(return_value={"q": "test"})
        ))
        self.assertIsInstance(response, GallicaResponseWrapper)