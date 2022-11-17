import unittest
from unittest import TestCase
from unittest.mock import MagicMock
from gallicaGetter.parse.arkRecord import ArkRecord
from gallicaGetter.parse.groupedCountRecord import GroupedCountRecord
from gallicaGetter.parse.occurrenceRecord import OccurrenceRecord
from gallicaGetter.parse.paperRecord import PaperRecord
from gallicaGetter.parse.parseRecord import ParseArkRecord
from gallicaGetter.parse.parseRecord import ParseGroupedRecordCounts
from gallicaGetter.parse.parseRecord import ParseOccurrenceRecords
from gallicaGetter.parse.parseRecord import ParsePaperRecords
from gallicaGetter.parse.parseRecord import ParseContentRecord
from gallicaGetter.parse.parseRecord import buildParser


class TestParseRecord(TestCase):

    def setUp(self) -> None:
        self.parsers = [
            ParseArkRecord(MagicMock()),
            ParseOccurrenceRecords(MagicMock(), requestID=1, ticketID=1),
            ParsePaperRecords(MagicMock()),
            ParseContentRecord(MagicMock()),
            ParseGroupedRecordCounts(MagicMock(), requestID=1, ticketID=1),
        ]

    def test_build(self):
        self.assertIsInstance(buildParser('ark'), ParseArkRecord)
        self.assertIsInstance(buildParser('groupedCount', requestID=1, ticketID=1), ParseGroupedRecordCounts)
        self.assertIsInstance(buildParser('occurrence', requestID=1, ticketID=1), ParseOccurrenceRecords)
        self.assertIsInstance(buildParser('paper'), ParsePaperRecords)
        self.assertIsInstance(buildParser('content'), ParseContentRecord)

    def test_responds_to_parseResponsesToRecords(self):
        [self.assertTrue(hasattr(parser, 'parseResponsesToRecords')) for parser in self.parsers]


class TestParseArkRecord(unittest.TestCase):

    def setUp(self) -> None:
        self.parser = ParseArkRecord(MagicMock())

    def test_parseResponsesToRecords(self):
        testResultGenerator = self.parser.parseResponsesToRecords(
            [
                MagicMock(),
                MagicMock(),
            ]
        )
        for testResult in testResultGenerator:
            self.assertIsInstance(testResult, ArkRecord)


class TestParseGroupedRecordCounts(unittest.TestCase):

    def setUp(self) -> None:
        self.testParse = ParseGroupedRecordCounts(
            parser=MagicMock(),
            ticketID='test',
            requestID='test'
        )

    def test_parse(self):
        test = self.testParse.parseResponsesToRecords(
            [
                MagicMock(),
                MagicMock(),
            ]
        )
        for testResult in test:
            self.assertIsInstance(testResult, GroupedCountRecord)


class TestParseOccurrenceRecords(unittest.TestCase):

    def setUp(self) -> None:
        self.testParse = ParseOccurrenceRecords(
            parser=MagicMock(),
            requestID=1,
            ticketID=1
        )

    def test_parseResponsesToRecords(self):
        testResponses = [
            MagicMock(),
            MagicMock(),
        ]
        self.testParse.parser.return_value = ['test1', 'test2']
        testResults = self.testParse.parseResponsesToRecords(testResponses)
        for result in testResults:
            self.assertIsInstance(result, OccurrenceRecord)


class TestParsePaperRecords(unittest.TestCase):

    def setUp(self) -> None:
        self.testParse = ParsePaperRecords(
            parser=MagicMock()
        )

    def test_parseResponsesToRecords(self):
        responses = [
            MagicMock(),
            MagicMock(),
        ]
        self.testParse.parser.getRecordsFromXML.return_value = [
            'record1',
            'record2',
        ]

        test = self.testParse.parseResponsesToRecords(responses)

        for testResult in test:
            self.assertIsInstance(testResult, PaperRecord)


class TestParseContentRecord(unittest.TestCase):

        def setUp(self) -> None:
            self.testParse = ParseContentRecord(
                parser=MagicMock()
            )

        def test_parseResponsesToRecords(self):
            responses = [
                MagicMock(),
                MagicMock(),
            ]
            self.testParse.parser.getNumResultsAndPagesForOccurrenceInPeriodical.return_value = [
                2,
                'test',
            ]

            test = self.testParse.parseResponsesToRecords(responses)

            for testResult in test:
                self.assertEqual(testResult.num_results, 2)
                self.assertEqual(testResult.get_pages(), 'test')
