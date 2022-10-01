from unittest import TestCase
from papersearchrunner import PaperSearchRunner
from unittest.mock import MagicMock, call


class TestPaperSearchRunner(TestCase):

    def setUp(self):
        self.testSearch = PaperSearchRunner(
            parse=MagicMock(),
            sruFetch=MagicMock(),
            paperQueryFactory=MagicMock(),
            arkFetch=MagicMock(),
            insert=MagicMock()
        )

        self.productionAddCodes = self.testSearch.addRecordDataForTheseCodesToDB
        self.testSearch.addRecordDataForTheseCodesToDB = MagicMock()

        self.productionAddAllFetchableRecords = self.testSearch.addAllFetchableRecordsToDB
        self.testSearch.addAllFetchableRecordsToDB = MagicMock()

        self.productionDoSearch = self.testSearch.doSearch
        self.testSearch.doSearch = MagicMock()

        self.productionGetPublishingYears = self.testSearch.getPublishingYearsForRecords
        self.testSearch.getPublishingYearsForRecords = MagicMock()

        self.productionAddPublishingYears = self.testSearch.addPublishingYearsToPaperRecord
        self.testSearch.addPublishingYearsToPaperRecord = MagicMock()

    def test_add_record_data_for_these_codes_to_db(self):
        self.productionAddCodes(['code1', 'code2'])

        self.testSearch.queryFactory.buildSRUqueriesForCodes.assert_called_once_with(['code1', 'code2'])
        self.testSearch.doSearch.assert_called_once_with(
            self.testSearch.queryFactory.buildSRUqueriesForCodes.return_value)

    def test_add_all_fetchable_records_to_db(self):
        self.testSearch.addAllFetchableRecordsToDB = self.productionAddAllFetchableRecords

        self.testSearch.addAllFetchableRecordsToDB()

        self.testSearch.queryFactory.buildSRUqueriesForAllRecords.assert_called_once_with()
        self.testSearch.doSearch.assert_called_once_with(
            self.testSearch.queryFactory.buildSRUqueriesForAllRecords.return_value)

    def test_do_search(self):
        self.productionDoSearch(['query1', 'query2'])

        self.testSearch.SRUfetch.fetchNoTrack.assert_has_calls([
            call('query1'),
            call('query2')
        ])
        self.testSearch.getPublishingYearsForRecords.assert_called_with(
            self.testSearch.convertResponseToRecords.return_value)
        self.testSearch.insertIntoPapers.assert_called_with(
            self.testSearch.getPublishingYearsForRecords.return_value)

    def test_convert_queries_to_records(self):
        queries = [
            MagicMock(responseXML='xml1'),
            MagicMock(responseXML='xml2')
            ]
        self.testSearch.parse.papers.side_effect = lambda x: [x]

        result = list(self.productionConvertQueries(queries))

        self.assertListEqual(result, ['xml1', 'xml2'])

    def test_get_publishing_years_for_records(self):
        self.testSearch.getPublishingYearsForRecords = self.productionGetPublishingYears

        self.testSearch.getPublishingYearsForRecords(
            [MagicMock(code='code1'),
            MagicMock(code='code2')]
        )

        self.testSearch.queryFactory.buildArkQueriesForCodes.assert_called_once()
        self.testSearch.ARKfetch.fetchNoTrack.assert_called_once_with(
            self.testSearch.queryFactory.buildArkQueriesForCodes.return_value
        )
        self.testSearch.addPublishingYearsToPaperRecord.assert_called_once()

    def test_add_publishing_years_to_paper_record(self):
        testYearQueries = [
            MagicMock(cql='/test1/date'),
            MagicMock(cql='/test2/date')
        ]
        testRecords = [
            MagicMock(code='test1'),
            MagicMock(code='test2')
        ]

        result = list(self.productionAddPublishingYears(
            testRecords,
            testYearQueries
        ))

        self.assertEqual(
            result[0].publishingYears,
            self.testSearch.parse.yearsPublished.return_value
        )
        self.assertEqual(
            result[1].publishingYears,
            self.testSearch.parse.yearsPublished.return_value
        )

