from unittest import TestCase
from unittest.mock import MagicMock
from gallica.getandput import GetAndPut


class TestSearch(TestCase):

    def setUp(self) -> None:
        self.search = GetAndPut(
            queries=['foo', 'bar'],
            insertRecordsIntoDatabase=MagicMock(),
            recordGetter=MagicMock(),
            searchType='foo',
            ticketID='bar'
        )

    def test_run(self):
        self.search.run()

        self.search.recordGetter.getFromQueries.assert_called_once_with(['foo', 'bar'])
        self.search.insertRecordsIntoDatabase.assert_called_once()

    def test_get_num_records_to_be_inserted(self):
        self.search.numRecordsToPutInDB = 42

        self.assertEqual(self.search.getNumRecordsToBeInserted(), 42)