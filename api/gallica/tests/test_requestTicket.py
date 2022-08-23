from unittest import TestCase
from unittest.mock import MagicMock, patch
from gallica.requestTicket import RequestTicket

import gallica.requestTicket


class TestRequestTicket(TestCase):

    @patch("gallica.requestTicket.RequestTicket.initQueryObjects")
    @patch("gallica.requestTicket.RequestTicket.sumResultsOfEachQuery")
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
    @patch("gallica.requestTicket.RequestTicket.sumResultsOfEachQuery")
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

    @patch("gallica.gallicaNgramOccurrenceQuery.GallicaNgramOccurrenceQuerySelectPapers.buildQuery")
    @patch("gallica.gallicaNgramOccurrenceQuery.GallicaNgramOccurrenceQuerySelectPapers.fetchNumTotalResults")
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

        self.assertIsInstance(testQuery, gallica.requestTicket.GallicaNgramOccurrenceQuerySelectPapers)
        self.assertEqual(testQuery.keyword, 'test')
        self.assertDictEqual(testQuery.papers, {"paper": "", "code": 'test'})
        self.assertFalse(testQuery.isYearRange)
        self.assertEqual(testQuery.ticketID, '')

    @patch("gallica.gallicaNgramOccurrenceQuery.GallicaNgramOccurrenceQueryAllPapers.buildQuery")
    @patch("gallica.gallicaNgramOccurrenceQuery.GallicaNgramOccurrenceQueryAllPapers.fetchNumTotalResults")
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

        self.assertIsInstance(testQuery, gallica.requestTicket.GallicaNgramOccurrenceQueryAllPapers)
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
        ticket.sumResultsOfEachQuery()

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

        ticket.updateProgressStats('the seattle times', 10, 50)

        ticket.progressThread.setTicketProgressStats.assert_called_with(
            "",
            {
                'progress': 30,
                'numResultsDiscovered': 0,
                'numResultsRetrieved': 150,
                'randomPaper': 'the seattle times',
                'estimateSecondsToCompletion': 7 / 50 * 10
            }
        )

        ticket.updateProgressStats('le figaro', 90, 50)

        ticket.progressThread.setTicketProgressStats.assert_called_with(
            "",
            {
                'progress': 40,
                'numResultsDiscovered': 0,
                'numResultsRetrieved': 200,
                'randomPaper': 'le figaro',
                'estimateSecondsToCompletion': 6 / 50 * 50
            }
        )



