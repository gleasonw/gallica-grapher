from unittest import TestCase
from unittest.mock import MagicMock, patch
from gallica.requestTicket import RequestTicket

import gallica.requestTicket


class TestRequestTicket(TestCase):

    @patch("gallica.requestTicket.RequestTicket.initQueryObjects")
    @patch("gallica.requestTicket.RequestTicket.sumResultsOfEachTicket")
    @patch("gallica.requestTicket.RequestTicket.startQueries")
    def test_run_all_paper_ticket(
            self,
            mock_startQueries,
            mock_getNumResults,
            mock_initQueryObjects):
        allPaperTicket = RequestTicket(
            {
                'terms': ['test'],
                'papersAndCodes': [],
                'dateRange': []
            },
            "",
            MagicMock(),
            MagicMock(),
            MagicMock())
        allPaperTicket.run()

        mock_initQueryObjects.assert_called_with(allPaperTicket.genAllPaperQuery)
        mock_getNumResults.assert_called_once()
        mock_startQueries.assert_called_once()

    @patch("gallica.requestTicket.RequestTicket.initQueryObjects")
    @patch("gallica.requestTicket.RequestTicket.sumResultsOfEachTicket")
    @patch("gallica.requestTicket.RequestTicket.startQueries")
    def test_run_select_paper_ticket(
            self,
            mock_startQueries,
            mock_getNumResults,
            mock_initQueryObjects):
        selectPaperTicket = RequestTicket(
            {
                'terms': ['test'],
                'papersAndCodes': ['test'],
                'dateRange': []
            },
            "",
            MagicMock(),
            MagicMock(),
            MagicMock())
        selectPaperTicket.run()

        mock_initQueryObjects.assert_called_with(selectPaperTicket.genSelectPaperQuery)
        mock_getNumResults.assert_called_once()
        mock_startQueries.assert_called_once()

    def test_init_query_objects(self):
        ticket = RequestTicket(
            {
                'terms': ['test'],
                'papersAndCodes': ['test'],
                'dateRange': []
            },
            "",
            MagicMock(),
            MagicMock(),
            MagicMock())
        ticket.keywords = [MagicMock, MagicMock, MagicMock]
        ticket.initQueryObjects(MagicMock(return_value=MagicMock()))
        self.assertEqual(len(ticket.keywordQueries), 3)

    @patch("gallica.keywordQuery.KeywordQuerySelectPapers.buildQuery")
    @patch("gallica.keywordQuery.KeywordQuerySelectPapers.fetchNumTotalResults")
    def test_gen_select_paper_query(self, mock_build, mock_fetch):
        ticket = RequestTicket(
            {
                'terms': ['test'],
                'papersAndCodes': {"paper": "", "code": 'test'},
                'dateRange': []
            },
            "",
            MagicMock(),
            MagicMock(),
            MagicMock())

        testQuery = ticket.genSelectPaperQuery(ticket.keywords[0])

        self.assertIsInstance(testQuery, gallica.requestTicket.KeywordQuerySelectPapers)
        self.assertEqual(testQuery.keyword, 'test')
        self.assertDictEqual(testQuery.papers, {"paper": "", "code": 'test'})
        self.assertFalse(testQuery.isYearRange)
        self.assertEqual(testQuery.ticketID, '')

    @patch("gallica.keywordQuery.KeywordQueryAllPapers.buildQuery")
    @patch("gallica.keywordQuery.KeywordQueryAllPapers.fetchNumTotalResults")
    def test_gen_all_paper_query(self, mock_build, mock_fetch):
        ticket = RequestTicket(
            {
                'terms': ['test'],
                'papersAndCodes': [],
                'dateRange': []
            },
            "",
            MagicMock(),
            MagicMock(),
            MagicMock())

        testQuery = ticket.genAllPaperQuery(ticket.keywords[0])

        self.assertIsInstance(testQuery, gallica.requestTicket.KeywordQueryAllPapers)
        self.assertEqual(testQuery.keyword, 'test')
        self.assertFalse(testQuery.isYearRange)
        self.assertEqual(testQuery.ticketID, '')

    def test_sum_results_of_each_ticket(self):
        ticket = RequestTicket(
            {
                'terms': ['test'],
                'papersAndCodes': [],
                'dateRange': []
            },
            "",
            MagicMock(),
            MagicMock(),
            MagicMock())
        ticket.keywordQueries=[
            MagicMock(getEstimateNumResults=
                      MagicMock(return_value=10)),
            MagicMock(getEstimateNumResults=
                      MagicMock(return_value=11)),
            MagicMock(getEstimateNumResults=
                      MagicMock(return_value=12))
        ]
        ticket.sumResultsOfEachTicket()

        self.assertEqual(ticket.totalResults, 33)

    def test_start_queries(self):
        ticket = RequestTicket(
            {
                'terms': ['test'],
                'papersAndCodes': [],
                'dateRange': []
            },
            "",
            MagicMock(),
            MagicMock(),
            MagicMock())
        ticket.keywordQueries = [
            MagicMock(runSearch=MagicMock()),
            MagicMock(runSearch=MagicMock()),
            MagicMock(runSearch=MagicMock())
        ]
        ticket.totalResults = 512

        ticket.startQueries()

        self.assertEqual(ticket.numBatches, 11)
        for query in ticket.keywordQueries:
            query.runSearch.assert_called_once()

    def test_update_progress(self):
        ticket = RequestTicket(
            {
                'terms': ['test'],
                'papersAndCodes': [],
                'dateRange': []
            },
            "",
            MagicMock(setProgress=MagicMock()),
            MagicMock(),
            MagicMock())
        ticket.numBatchesRetrieved = 2
        ticket.numBatches = 10

        ticket.updateProgress()

        ticket.progressThread.setProgress.assert_called_with(30)



