from gallicaGetter.fetch.get import Get, Response
from unittest.mock import MagicMock
from unittest import TestCase


class TestGet(TestCase):

    def setUp(self) -> None:
        self.getter = Get('test')

    def test_get(self):
        self.getter.http = MagicMock(request=MagicMock(
            return_value=MagicMock(status=200)))
        response = self.getter.get(MagicMock())
        self.assertIsInstance(response, Response)



