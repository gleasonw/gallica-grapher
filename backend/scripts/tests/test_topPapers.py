from unittest import TestCase
from unittest.mock import patch, MagicMock
from scripts.topPapers import TopPapers
from DBtester import DBtester


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
        continuousTopTest = TopPapers(
            ticketID="1",
            dateRange="1900,2000",
            continuous="true")
        sporadicTopTest = TopPapers(
            ticketID="1",
            dateRange="1900,2000",
            continuous="false"
        )
        continuousTopTest.selectTopPapers = MagicMock()
        continuousTopTest.selectTopContinuousPapers = MagicMock()
        sporadicTopTest.selectTopPapers = MagicMock()
        sporadicTopTest.selectTopContinuousPapers = MagicMock()

        continuousTopTest.getTopPapers()
        sporadicTopTest.getTopPapers()

        continuousTopTest.selectTopContinuousPapers.assert_called_once()
        sporadicTopTest.selectTopPapers.assert_called_once()

    def test_select_top_papers(self):
        testTopPapers = DBtester().getTestTopPapers(
            continuous='false',
            dateRange=''
        )

        firstPaperCount = testTopPapers[0][1]
        secondPaperCount = testTopPapers[1][1]
        self.assertEqual(len(testTopPapers), 2)
        self.assertEqual(firstPaperCount, 13)
        self.assertEqual(secondPaperCount, 5)


    def test_select_top_continuous_papers(self):
        testTopPapers = DBtester().getTestTopPapers(
            continuous='true',
            dateRange="1900,1907"
        )

        firstPaperCount = testTopPapers[0][1]

        self.assertEqual(len(testTopPapers), 1)
        self.assertEqual(firstPaperCount, 13)

