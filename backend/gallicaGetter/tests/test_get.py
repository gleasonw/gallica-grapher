from get import Get
from response import Response
from unittest.mock import MagicMock
from unittest import TestCase


class TestGet(TestCase):

    def setUp(self) -> None:
        self.getter = Get('test')

    def test_get(self):
        self.getter.http = MagicMock()
        response = self.getter.get(MagicMock())
        self.assertIsInstance(response, Response)



