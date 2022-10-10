from gallica.paperSearch import PaperSearch
from gallica.factories.paperSearchFactory import PaperSearchFactory
import unittest
from unittest.mock import MagicMock


class TestPaperSearchFactory(unittest.TestCase):

        def setUp(self) -> None:
            self.testFactory = PaperSearchFactory(
                parse=MagicMock(),
                SRUapi=MagicMock()
            )

        def test_buildPaperSearch(self):
            self.assertIsInstance(self.testFactory.buildSearch(), PaperSearch)