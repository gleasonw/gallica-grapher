from unittest import TestCase
from unittest.mock import MagicMock, patch
from ticket import Ticket

import ticket


class TestTicket(TestCase):

    def setUp(self) -> None:
        self.testTicketInstance = Ticket(
            {
                'terms': ['test'],
                'papersAndCodes': [{'code': 'test', 'name': 'test'}],
                'dateRange': []
            },
            "",
            "",
            MagicMock(),
            MagicMock(),
            MagicMock()
        )
        self.testTicketInstance.estimateTotalResults = 512

    @patch('scripts.ticket.Ticket.initQueryObjects')
    @patch('scripts.ticket.Ticket.sumResultsOfEachQuery')
    def test_get_estimate_number_records(self, mock_sum_results, mock_init):
        self.testTicketInstance.papersAndCodes = []

        result = self.testTicketInstance.getEstimateNumberRecords()

        self.assertEqual(result, 512)
        mock_sum_results.assert_called_once()
        mock_init.assert_called_with(self.testTicketInstance.genAllPaperQuery)

    @patch('scripts.ticket.Ticket.initQueryObjects')
    @patch('scripts.ticket.Ticket.sumResultsOfEachQuery')
    def test_get_estimate_number_records_select_paper_ticket(self, mock_sum_results, mock_init):
        self.testTicketInstance.papersAndCodes = [{'code': 'test', 'name': 'test'}]
        result = self.testTicketInstance.getEstimateNumberRecords()

        self.assertEqual(result, 512)
        mock_sum_results.assert_called_once()
        mock_init.assert_called_with(self.testTicketInstance.genSelectPaperQuery)

    def test_init_query_objects(self):
        self.testTicketInstance.terms = [MagicMock, MagicMock, MagicMock]
        self.testTicketInstance.initQueryObjects(MagicMock(return_value=MagicMock()))
        self.assertEqual(len(self.testTicketInstance.termQueries), 3)

    @patch("scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.fetchNumTotalResults")
    def test_gen_select_paper_query(self, mock_fetch):
        self.testTicketInstance.terms = ['test']
        testQuery = self.testTicketInstance.genSelectPaperQuery(self.testTicketInstance.terms[0])

        self.assertIsInstance(testQuery, ticket.QueriesSelectPapers)
        self.assertEqual(testQuery.keyword, 'test')
        self.assertListEqual(testQuery.paperCodes, ['test'])
        self.assertFalse(testQuery.isYearRange)
        self.assertEqual(testQuery.ticketID, '')

    @patch("scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencyAllPapers.fetchNumTotalResults")
    def test_gen_all_paper_query(self, mock_fetch):
        testQuery = self.testTicketInstance.genAllPaperQuery(self.testTicketInstance.terms[0])

        self.assertIsInstance(testQuery, ticket.QueriesAllPapers)
        self.assertEqual(testQuery.keyword, 'test')
        self.assertFalse(testQuery.isYearRange)
        self.assertEqual(testQuery.ticketID, '')

    def test_sum_results_of_each_ticket(self):
        self.testTicketInstance.estimateTotalResults = 0
        self.testTicketInstance.termQueries = [
            MagicMock(getEstimateNumResults=
                      MagicMock(return_value=10)),
            MagicMock(getEstimateNumResults=
                      MagicMock(return_value=11)),
            MagicMock(getEstimateNumResults=
                      MagicMock(return_value=12))
        ]
        self.testTicketInstance.getNumRecords()

        self.assertEqual(self.testTicketInstance.estimateTotalResults, 33)

    def test_update_progress(self):
        self.testTicketInstance.estimateTotalResults = 0
        self.testTicketInstance.numBatchesRetrieved = 2
        self.testTicketInstance.numBatches = 10

        self.testTicketInstance.updateProgressStats('the seattle times', 10, 50)

        self.testTicketInstance.progressThread.setTicketProgressStats.assert_called_with(
            "",
            {
                'progress': 30,
                'numResultsDiscovered': 0,
                'numResultsRetrieved': 150,
                'randomPaper': 'the seattle times',
                'estimateSecondsToCompletion': 7 / 50 * 10
            }
        )

        self.testTicketInstance.updateProgressStats('le figaro', 90, 50)

        self.testTicketInstance.progressThread.setTicketProgressStats.assert_called_with(
            "",
            {
                'progress': 40,
                'numResultsDiscovered': 0,
                'numResultsRetrieved': 200,
                'randomPaper': 'le figaro',
                'estimateSecondsToCompletion': 6 / 50 * 50
            }
        )



