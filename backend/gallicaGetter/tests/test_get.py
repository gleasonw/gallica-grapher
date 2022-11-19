from gallicaGetter.fetch.gallicasession import GallicaSession, Response
from unittest.mock import MagicMock
from unittest import TestCase


class TestGet(TestCase):

    def setUp(self) -> None:
        self.getter = GallicaSession('test')

    def test_get(self):
        self.getter.session = MagicMock(request=MagicMock(
            return_value=MagicMock(status=200)))
        response = self.getter.get(MagicMock())
        self.assertIsInstance(response, Response)



