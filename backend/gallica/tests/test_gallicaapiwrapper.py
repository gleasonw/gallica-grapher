from unittest.mock import MagicMock
from unittest import TestCase
from gallicaResponse import GallicaResponse
from get import Get


class TestGallicaAPIWrapper(TestCase):

    def setUp(self) -> None:
        self.gallicaAPIWrapper = Get(baseUrl="https://gallica.bnf.fr/SRU")

    def test_get(self):
        self.gallicaAPIWrapper.http = MagicMock()
        response = self.gallicaAPIWrapper.get(query=MagicMock(
            getFetchParams=MagicMock(return_value={"q": "test"})
        ))
        self.assertIsInstance(response, GallicaResponse)