from unittest import TestCase
from request import Request
from unittest.mock import MagicMock, call
from request import RECORD_LIMIT, MAX_DB_SIZE


class TestRequest(TestCase):

    def setUp(self) -> None:
        self.testRequest = Request(
            requestID='testrequest',
            ticketSearches=
                [
                    MagicMock(
                        getEstimateNumResultsForTicket=MagicMock(return_value=2),
                        getTicketID=MagicMock(return_value='testticket1'),
                    ),
                    MagicMock(
                        getEstimateNumResultsForTicket=MagicMock(return_value=3),
                        getTicketID=MagicMock(return_value='testticket2'),
                    ),
                ],
            dbConn=MagicMock()
        )

        self.productionRun = self.testRequest.run
        self.testRequest.run = MagicMock()

        self.productionEstimateIsUnderLimit = self.testRequest.estimateIsUnderLimit
        self.testRequest.estimateIsUnderLimit = MagicMock()

        self.productionGetNumberRowsInAllTables = self.testRequest.getNumberRowsStoredInAllTables
        self.testRequest.getNumberRowsStoredInAllTables = MagicMock()

        self.productionDoAllSearches = self.testRequest.doAllSearches
        self.testRequest.doAllSearches = MagicMock()

        self.productionInitProgressStats = self.testRequest.initProgressStats
        self.testRequest.initProgressStats = MagicMock()

        self.productionSetTicketProgressTo100AndMarkAsDone = self.testRequest.setTicketProgressTo100AndMarkAsDone
        self.testRequest.setTicketProgressTo100AndMarkAsDone = MagicMock()

        self.productionSetTicketProgressStats = self.testRequest.setTicketProgressStats
        self.testRequest.setTicketProgressStats = MagicMock()

    def test_run(self):
        self.testRequest.estimateIsUnderLimit.return_value=True

        self.productionRun()

        self.testRequest.initProgressStats.assert_called_once()
        self.testRequest.estimateIsUnderLimit.assert_called_with(5)
        self.testRequest.doAllSearches.assert_called_once()
        self.testRequest.DBconnection.close.assert_called_once()

    def test_init_progress_stats(self):
        testProgressStats = self.productionInitProgressStats()

        self.assertDictEqual(
            testProgressStats,
            {
                'testticket1': {
                    'progress': 0,
                    'numResultsDiscovered': 0,
                    'numResultsRetrieved': 0,
                    'randomPaper': None,
                    'estimateSecondsToCompletion': 0
                },
                'testticket2': {
                    'progress': 0,
                    'numResultsDiscovered': 0,
                    'numResultsRetrieved': 0,
                    'randomPaper': None,
                    'estimateSecondsToCompletion': 0
                }
            }
        )

    def test_estimate_is_under_limit_given_true(self):
        self.testRequest.getNumberRowsStoredInAllTables.return_value = 10000

        self.assertTrue(self.productionEstimateIsUnderLimit(9999))

    def test_estimate_is_under_limit_given_record_limit_exceeded(self):
        self.testRequest.getNumberRowsStoredInAllTables.return_value = 0

        self.assertFalse(self.productionEstimateIsUnderLimit(RECORD_LIMIT + 1))

    def test_estimate_is_under_limit_given_db_limit_exceeded(self):
        self.testRequest.getNumberRowsStoredInAllTables.return_value = MAX_DB_SIZE - 10000

        self.assertFalse(self.productionEstimateIsUnderLimit(1))

    def test_get_number_rows_stored_in_all_tables(self):
        self.testRequest.DBconnection.cursor.return_value.__enter__.return_value.execute = MagicMock()

        self.productionGetNumberRowsInAllTables()

        self.testRequest.DBconnection.cursor.return_value.__enter__.return_value.execute.assert_called_once_with(
                """
                SELECT sum(reltuples)::bigint AS estimate
                FROM pg_class
                WHERE relname IN ('results', 'papers');
                """
        )

    def test_do_all_searches(self):
        self.productionDoAllSearches()

        for searchHandler in self.testRequest.ticketSearches:
            searchHandler.run.assert_called_once()
            searchHandler.setProgressCallback.assert_called_once_with(
                self.testRequest.setTicketProgressStats
            )
        self.assertTrue(self.testRequest.finished)

    def test_set_ticket_progress_stats(self):
        self.productionInitProgressStats()
        self.productionSetTicketProgressStats('testticket1', 'test')
        self.productionSetTicketProgressStats('testticket2', 'test')

        self.assertDictEqual(
            self.testRequest.ticketProgressStats,
            {
                'testticket1': 'test',
                'testticket2': 'test'
            }
        )

    def test_set_ticket_progress_to_100_and_mark_as_done(self):
        testSearch = MagicMock(
            getTicketID=MagicMock(return_value='testticket1'),
            getNumRetrieved=MagicMock(return_value=1),
        )

        self.productionSetTicketProgressTo100AndMarkAsDone(testSearch)

        self.testRequest.setTicketProgressStats.assert_called_once_with(
            'testticket1',
            {
                'progress': 100,
                'numResultsDiscovered': 1,
                'numResultsRetrieved': 1,
                'randomPaper': None,
                'estimateSecondsToCompletion': 0
            }
        )




