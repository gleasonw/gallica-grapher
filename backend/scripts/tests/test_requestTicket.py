from unittest import TestCase
from unittest.mock import MagicMock, patch
from scripts.requestTicket import RequestTicket

import scripts.requestTicket


class TestRequestTicket(TestCase):

    @patch("scripts.requestTicket.RequestTicket.initQueryObjects")
    @patch("scripts.requestTicket.RequestTicket.sumResultsOfEachQuery")
    @patch("scripts.requestTicket.RequestTicket.startQueries")
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

    @patch("scripts.requestTicket.RequestTicket.initQueryObjects")
    @patch("scripts.requestTicket.RequestTicket.sumResultsOfEachQuery")
    @patch("scripts.requestTicket.RequestTicket.startQueries")
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
        ticket.terms = [MagicMock, MagicMock, MagicMock]
        ticket.initQueryObjects(MagicMock(return_value=MagicMock()))
        self.assertEqual(len(ticket.termQueries), 3)

    @patch("scripts.gallicaNgramOccurrenceQuery.GallicaNgramOccurrenceQuerySelectPapers.buildQuery")
    @patch("scripts.gallicaNgramOccurrenceQuery.GallicaNgramOccurrenceQuerySelectPapers.fetchNumTotalResults")
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

        testQuery = ticket.genSelectPaperQuery(ticket.terms[0])

        self.assertIsInstance(testQuery, scripts.requestTicket.GallicaNgramOccurrenceQuerySelectPapers)
        self.assertEqual(testQuery.keyword, 'test')
        self.assertDictEqual(testQuery.papers, {"paper": "", "code": 'test'})
        self.assertFalse(testQuery.isYearRange)
        self.assertEqual(testQuery.ticketID, '')

    @patch("scripts.gallicaNgramOccurrenceQuery.GallicaNgramOccurrenceQueryAllPapers.buildQuery")
    @patch("scripts.gallicaNgramOccurrenceQuery.GallicaNgramOccurrenceQueryAllPapers.fetchNumTotalResults")
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

        testQuery = ticket.genAllPaperQuery(ticket.terms[0])

        self.assertIsInstance(testQuery, scripts.requestTicket.GallicaNgramOccurrenceQueryAllPapers)
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
        ticket.termQueries=[
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
        ticket.termQueries = [
            MagicMock(runSearch=MagicMock()),
            MagicMock(runSearch=MagicMock()),
            MagicMock(runSearch=MagicMock())
        ]
        ticket.totalResults = 512

        ticket.startQueries()

        self.assertEqual(ticket.numBatches, 11)
        for query in ticket.termQueries:
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



