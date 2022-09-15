from unittest import TestCase
from ticketsearchrunner import TicketSearchRunner
from unittest.mock import MagicMock, call


class TestTicketSearchRunner(TestCase):

    def setUp(self) -> None:
        self.testSearch = TicketSearchRunner(
            parse=MagicMock(),
            ticket=MagicMock(
                key='testKey',
                terms=['term1', 'term2'],
                codes=['code1', 'code2'],
                startYear='startYear',
                endYear='endYear',
                queries=[['query1'], ['query2']],
                estimateNumResults=2,
            ),
            requestID='testRequest',
            schemaLink=MagicMock(),
            sruFetch=MagicMock(),
            paperAdd=MagicMock()
        )
        self.productionSearch = self.testSearch.search
        self.testSearch.search = MagicMock()

        self.productionRemoveDuplicates = self.testSearch.removeDuplicateRecords
        self.testSearch.removeDuplicateRecords = MagicMock()

        self.productionInsertMissingPapersToDB = self.testSearch.insertMissingPapersToDB
        self.testSearch.insertMissingPapersToDB = MagicMock()

        self.productionSetProgressTracker = self.testSearch.setProgressTracker
        self.testSearch.setProgressTracker = MagicMock()

        self.productionProgressTrackWithPaper = self.testSearch.progressTrackWithPaper
        self.testSearch.progressTrackWithPaper = MagicMock()

    def test_search(self):
        self.testSearch.queries = [['query1'], ['query2']]
        self.testSearch.search = self.productionSearch

        self.testSearch.search()

        self.testSearch.SRUfetch.fetchAllAndTrackProgress.assert_has_calls([
            call(['query1'], self.testSearch.progressTrackWithPaper),
            call(['query2'], self.testSearch.progressTrackWithPaper),
        ])
        self.testSearch.removeDuplicateRecords.assert_called()
        self.testSearch.insertMissingPapersToDB.assert_called()
        self.testSearch.schema.insertRecordsIntoResults.assert_called()
        self.testSearch.schema.fetchNumResultsForQueries.assert_called_with(
            self.testSearch.ticket.key
        )
        self.testSearch.ticket.setNumResultsRetrieved.assert_called_once_with(
            self.testSearch.schema.fetchNumResultsForQueries.return_value
        )

    def test_removeDuplicateRecords(self):
        self.testSearch.removeDuplicateRecords = self.productionRemoveDuplicates

        records = [
            MagicMock(uniquenessCheck='a'),
            MagicMock(uniquenessCheck='b'),
            MagicMock(uniquenessCheck='a'),
            MagicMock(uniquenessCheck='c'),
            MagicMock(uniquenessCheck='b'),
        ]
        uniqueRecords = list(self.testSearch.removeDuplicateRecords(records))

        self.assertEqual(uniqueRecords, [records[0], records[1], records[3]])

    def test_insertMissingPapersToDB(self):
        self.testSearch.insertMissingPapersToDB = self.productionInsertMissingPapersToDB

        records = [
            MagicMock(code='a'),
            MagicMock(code='b'),
            MagicMock(code='a'),
            MagicMock(code='c'),
            MagicMock(code='b'),
        ]
        self.testSearch.schema.getPaperCodesThatMatch.return_value = ['a', 'b']
        self.testSearch.insertMissingPapersToDB(records)

        self.testSearch.addTheseCodesToDB.assert_called_with({'c'})

    def test_progressTrackWithPaper(self):
        self.testSearch.progressTrackWithPaper = self.productionProgressTrackWithPaper

        query = MagicMock()
        numWorkers = MagicMock()
        self.testSearch.parse.onePaperTitleFromOccurrenceBatch.return_value = 'paper'
        self.testSearch.onUpdateProgress = MagicMock()
        self.testSearch.progressTrackWithPaper(query, numWorkers)

        self.testSearch.parse.onePaperTitleFromOccurrenceBatch.assert_called_with(query.responseXML)
        self.testSearch.onUpdateProgress.assert_called_with(
            query=query,
            numWorkers=numWorkers,
            randomPaper='paper'
        )



