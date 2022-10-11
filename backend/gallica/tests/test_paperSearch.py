from unittest import TestCase
from unittest.mock import MagicMock
from gallica.paperSearch import PaperSearch


class TestPaperSearch(TestCase):

    def setUp(self) -> None:
        self.paperSearch = PaperSearch(
            SRURecordGetter=MagicMock(),
            ARKRecordGetter=MagicMock(),
            queryMaker=MagicMock(),
            insertIntoPapers=MagicMock()
        )
        self.paperSearch.composeRecords = MagicMock()

    #Experimenting with test design. This might be silly -- just test for calls as in the other test?
    def test_get_records_for_these_codes(self):
        self.paperSearch.queryMaker.buildSRUQueriesForCodes.side_effect = lambda x: x
        self.paperSearch.queryMaker.buildArkQueriesForCodes.side_effect = lambda x: x
        self.paperSearch.SRURecordGetter.getFromQueries.side_effect = lambda x: x
        self.paperSearch.ARKRecordGetter.getFromQueries.side_effect = lambda x: x
        self.paperSearch.composeRecords.side_effect = lambda x, y: x + y

        codes = [1, 2, 3]
        result = self.paperSearch.getRecordsForTheseCodes(codes)

        self.assertEqual(result, codes + codes)

    def test_put_all_paper_records_into_db(self):

        self.paperSearch.putAllPaperRecordsIntoDB()

        self.paperSearch.queryMaker.buildSRUQueriesForAllRecords.assert_called_once()
        self.paperSearch.SRURecordGetter.getFromQueries.assert_called_once()
        self.paperSearch.queryMaker.buildArkQueriesForCodes.assert_called_once()
        self.paperSearch.ARKRecordGetter.getFromQueries.assert_called_once()
        self.paperSearch.composeRecords.assert_called_once()
        self.paperSearch.insertIntoPapers.assert_called_once()