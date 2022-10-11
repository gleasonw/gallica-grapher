from unittest import TestCase
from unittest.mock import MagicMock
from gallica.recordGetter import RecordGetter


class TestRecordGetter(TestCase):

    def setUp(self) -> None:
        self.recordGetter = RecordGetter(
            gallicaAPI=MagicMock(),
            parseData=MagicMock(),
            onUpdateProgress=MagicMock()
        )

    def test_get_from_queries(self):
        self.recordGetter.getFromQueries(queries=[])

        self.recordGetter.gallicaAPI.fetchAll.assert_called_once()
        self.recordGetter.parser.parseResponsesToRecords.assert_called_once()