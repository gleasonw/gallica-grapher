from unittest import TestCase
from unittest.mock import patch, MagicMock
from gallica.topPapers import TopPapers


class TestTopPapers(TestCase):

    def test_init_top_papers(self):
        cleanTopTest = TopPapers(
            ticketID="1",
            dateRange="1900,2000",
            continuous="true")

        self.assertEqual(cleanTopTest.ticketID, "1")
        self.assertEqual(cleanTopTest.continuous, True)
        self.assertEqual(cleanTopTest.lowYear, "1900")
        self.assertEqual(cleanTopTest.highYear, "2000")

        messyTopTest = TopPapers(
            ticketID="1",
            dateRange="",
            continuous="truee")

        self.assertEqual(messyTopTest.ticketID, "1")
        self.assertEqual(messyTopTest.continuous, False)

    def test_get_top_papers(self):
        self.fail()

    def test_select_top_papers(self):
        self.fail()

    def test_select_top_continuous_papers(self):
        self.fail()
