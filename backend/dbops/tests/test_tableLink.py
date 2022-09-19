from dbops.schemaLinkForSearch import SchemaLinkForSearch
from unittest import TestCase
from unittest.mock import MagicMock, Mock, call
from DBtester import DBtester
from gallica.dto.paperRecord import PaperRecord
from gallica.dto.occurrenceRecord import OccurrenceRecord
from schemaLinkForSearch import CSVStream


class TestTableLink(TestCase):

    def setUp(self):
        self.testTransaction = SchemaLinkForSearch(
            MagicMock(),
            'testrequest'
        )
        self.testTransaction.CSVstreamBuilder = MagicMock()

        self.productionInsertRecordsIntoPapers = self.testTransaction.insertRecordsIntoPapers
        self.testTransaction.insertRecordsIntoPapers = MagicMock()

        self.productionInsertRecordsIntoResults = self.testTransaction.insertRecordsIntoResults
        self.testTransaction.insertRecordsIntoResults = MagicMock()

        self.productionGetPaperCodesThatMatch = self.testTransaction.getPaperCodesThatMatch
        self.testTransaction.getPaperCodesThatMatch = MagicMock()

    def test_insertRecordsIntoPapers(self):
        records = ['testrecord', 'testrecord2']

        self.productionInsertRecordsIntoPapers(records)

        self.testTransaction.CSVstreamBuilder.assert_called_once()
        self.testTransaction.conn.cursor.return_value.copy_from.assert_called_with(
            self.testTransaction.CSVstreamBuilder.return_value,
            'papers',
            sep='|'
        )

    def test_insertRecordsIntoResults(self):
        records = ['testrecord', 'testrecord2']

        self.productionInsertRecordsIntoResults(records)

        self.testTransaction.CSVstreamBuilder.assert_called_once()
        self.testTransaction.conn.cursor.return_value.copy_from.assert_called_with(
            self.testTransaction.CSVstreamBuilder.return_value,
            'results',
            sep='|'
        )

    def test_getPaperCodesThatMatch(self):
        codes = ['testcode', 'testcode2']

        self.productionGetPaperCodesThatMatch(codes)

        self.testTransaction.conn.cursor.return_value.execute.assert_called_with(
            'SELECT code FROM papers WHERE code IN %s',
            (tuple(codes),)
        )


class TestCSVStream(TestCase):

    def setUp(self) -> None:
        self.testStream = CSVStream()

        self.generateCSV = self.testStream.generateCSVstreamFromRecords
        self.testStream.generateCSVstreamFromRecords = MagicMock()

        self.cleanCSV = self.testStream.cleanCSVrow
        self.testStream.cleanCSVrow = MagicMock()

    def test_generateCSVstreamFromRecords(self):
        records = [
            MagicMock(
                getRow=MagicMock(
                    return_value=('nice', 'nice')
                ),
            ),
            MagicMock(
                getRow=MagicMock(
                    return_value=('nice2', 'nice2')
                )
            )
        ]
        self.testStream.cleanCSVrow.side_effect = lambda x: x

        result = self.generateCSV(records)

        self.testStream.cleanCSVrow.assert_has_calls(
            [call('nice'),
             call('nice'),
             call('nice2'),
             call('nice2')]
        )
        self.assertEqual(
            result.getvalue(),
            'nice|nice\nnice2|nice2\n'
        )

    def test_cleanCSVrow(self):
        self.assertEqual(
            self.cleanCSV('nice|nice'),
            'nice\\|nice'
        )
        self.assertEqual(
            self.cleanCSV(None),
            '\\N'
        )
        self.assertEqual(
            self.cleanCSV('nice'),
            'nice'
        )

    @staticmethod
    def get5MockKeywordRecords():
        payload = []
        ngrams = ['t', 'te', 'ter', 'term', 'term!']
        codes = ['a', 'b', 'c', 'd', 'e']
        ticketIDs = ['1', '2', '3', '4', '5']
        for i in range(5):
            mockRecord = Mock()
            mockRecord.__class__ = OccurrenceRecord
            mockRecord.getDate = MagicMock(return_value=[1920, 10, 1])
            mockRecord.getUrl = MagicMock(return_value='1234.com')
            mockRecord.getKeyword = MagicMock(return_value=ngrams[i])
            mockRecord.getPaperCode = MagicMock(return_value=codes[i])
            mockRecord.getTicketID = MagicMock(return_value=ticketIDs[i])
            payload.append(mockRecord)

        return payload

    @staticmethod
    def get5MockPaperRecords():
        payload = []
        codes = ['a', 'b', 'c', 'd', 'e']
        for i in range(5):
            mockRecord = Mock()
            mockRecord.__class__ = PaperRecord
            mockRecord.getPaperCode = MagicMock(return_value=codes[i])
            mockRecord.getPaperTitle = MagicMock(return_value='tests title')
            mockRecord.isContinuous = MagicMock(return_value=True)
            mockRecord.getDate = MagicMock(return_value=[1920, 1930])
            payload.append(mockRecord)

        return payload
