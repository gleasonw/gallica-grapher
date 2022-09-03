from unittest import TestCase
from unittest.mock import MagicMock, patch
from scripts.ticket import Ticket

import scripts.ticket


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
        self.testTicketInstance.totalResults = 512

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

    @patch("scripts.ticket.Ticket.addKeywordAndTicketIDToRecords")
    def test_run(self, mock_add):
        self.testTicketInstance.termQueries = [
            MagicMock(runSearch=MagicMock()),
            MagicMock(runSearch=MagicMock()),
            MagicMock(runSearch=MagicMock())
        ]
        mock_add.return_value = [1, 2, 3]

        self.testTicketInstance.run()

        self.assertEqual(self.testTicketInstance.numBatches, 11)
        for query in self.testTicketInstance.termQueries:
            query.runSearch.assert_called_once()
        mock_add.assert_called()
        self.assertListEqual(self.testTicketInstance.records, [1, 2, 3, 1, 2, 3, 1, 2, 3])

    def test_add_keyword_and_ticket_id_to_records(self):
        self.testTicketInstance.ticketID = 'self.testTicketInstanceID'
        mockRecord = MagicMock(
            setKeyword=MagicMock(),
            setTicketID=MagicMock())
        testRecords = [mockRecord, mockRecord, mockRecord]

        modifiedRecords = self.testTicketInstance.addKeywordAndTicketIDToRecords(testRecords, 'test')

        mockRecord.setKeyword.assert_called_with('test')
        mockRecord.setTicketID.assert_called_with('self.testTicketInstanceID')
        self.assertEqual(len(modifiedRecords), 3)

    def test_init_query_objects(self):
        self.testTicketInstance.terms = [MagicMock, MagicMock, MagicMock]
        self.testTicketInstance.initQueryObjects(MagicMock(return_value=MagicMock()))
        self.assertEqual(len(self.testTicketInstance.termQueries), 3)

    @patch("scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.fetchNumTotalResults")
    def test_gen_select_paper_query(self, mock_fetch):
        self.testTicketInstance.terms = ['test']
        testQuery = self.testTicketInstance.genSelectPaperQuery(self.testTicketInstance.terms[0])

        self.assertIsInstance(testQuery, scripts.ticket.NgramQueryWithConcurrencySelectPapers)
        self.assertEqual(testQuery.keyword, 'test')
        self.assertListEqual(testQuery.paperCodes, ['test'])
        self.assertFalse(testQuery.isYearRange)
        self.assertEqual(testQuery.ticketID, '')

    @patch("scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencyAllPapers.fetchNumTotalResults")
    def test_gen_all_paper_query(self, mock_fetch):
        testQuery = self.testTicketInstance.genAllPaperQuery(self.testTicketInstance.terms[0])

        self.assertIsInstance(testQuery, scripts.ticket.NgramQueryWithConcurrencyAllPapers)
        self.assertEqual(testQuery.keyword, 'test')
        self.assertFalse(testQuery.isYearRange)
        self.assertEqual(testQuery.ticketID, '')

    def test_sum_results_of_each_ticket(self):
        self.testTicketInstance.totalResults = 0
        self.testTicketInstance.termQueries = [
            MagicMock(getEstimateNumResults=
                      MagicMock(return_value=10)),
            MagicMock(getEstimateNumResults=
                      MagicMock(return_value=11)),
            MagicMock(getEstimateNumResults=
                      MagicMock(return_value=12))
        ]
        self.testTicketInstance.sumResultsOfEachQuery()

        self.assertEqual(self.testTicketInstance.totalResults, 33)

    def test_update_progress(self):
        self.testTicketInstance.totalResults = 0
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



