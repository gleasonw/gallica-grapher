from unittest import TestCase
from paperQueryFactory import PaperQueryFactory
from unittest.mock import MagicMock


class TestPaperQueryFactory(TestCase):

    def setUp(self) -> None:
        self.testFactory = PaperQueryFactory()
        self.testFactory.cql = MagicMock()
        self.testFactory.indexer = MagicMock()
        self.testFactory.queryBatcher = MagicMock()

        self.productionBuildSRU = self.testFactory.buildSRUQueriesForCodes
        self.testFactory.buildSRUQueriesForCodes = MagicMock()

        self.productionBuildARK = self.testFactory.buildARKQueriesForCodes
        self.testFactory.buildARKQueriesForCodes = MagicMock()

        self.productionBuildAllRecords = self.testFactory.buildAllRecordsQueries
        self.testFactory.buildAllRecordsQueries = MagicMock()

    def test_buildSRUQueriesForCodes(self):
        codes = ['code1', 'code2']
        codeGenerator = (code for code in codes)

        test = self.productionBuildSRU(codeGenerator)

        self.testFactory.cql.buildRequest.assert_called_once_with(codeGenerator)
        self.testFactory.indexer.addQueriesAndNumResultsToTicket.assert_called_with(
            self.testFactory.cql.buildRequest.return_value
        )
        self.testFactory.queryBatcher.assert_called_once()
        self.assertEqual(
            test,
            self.testFactory.queryBatcher.return_value
        )

    def test_buildARKQueriesForCodes(self):
        codes = ['code1', 'code2']
        codeGenerator = (code for code in codes)

        test = self.productionBuildARK(codeGenerator)

        self.testFactory.queryBatcher.assert_called_once()
        self.assertEqual(
            test,
            self.testFactory.queryBatcher.return_value
        )

    def test_buildAllRecordsQueries(self):
        test = self.productionBuildAllRecords()

        self.testFactory.indexer.addQueriesAndNumResultsToTicket.assert_called_with(
            ['dc.type all "fascicule" and ocrquality > "050.00"']
        )
        self.testFactory.queryBatcher.assert_called_once()
        self.assertEqual(
            test,
            self.testFactory.queryBatcher.return_value
        )

