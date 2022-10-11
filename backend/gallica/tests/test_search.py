from unittest import TestCase
from unittest.mock import MagicMock
from gallica.search import Search


class TestSearch(TestCase):

    def setUp(self) -> None:
        self.search = Search(
            queries=['foo', 'bar'],
            insertRecordsIntoDatabase=MagicMock(),
            recordGetter=MagicMock(),
        )

    def test_run(self):
        self.search.run()

        self.search.recordGetter.getFromQueries.assert_called_once_with(['foo', 'bar'])
        self.search.insertRecordsIntoDatabase.assert_called_once_with(self.search.recordGetter.getFromQueries.return_value)

    def test_run_with_on_adding_results_to_db(self):
        self.search.onAddingResultsToDB = MagicMock()

        self.search.run()

        self.search.onAddingResultsToDB.assert_called_once()

    def test_get_num_records_to_be_inserted(self):
        self.search.numRecordsToPutInDB = 42

        self.assertEqual(self.search.getNumRecordsToBeInserted(), 42)