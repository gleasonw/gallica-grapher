import unittest
from unittest import TestCase
from unittest.mock import MagicMock
from gallicaGetter.parse.record import (
    VolumeOccurrenceRecord,
    PeriodOccurrenceRecord,
    PaperRecord,
    ArkRecord,
    ContentRecord,
)
from gallicaGetter.parse.parseRecord import ParseArkRecord
from gallicaGetter.parse.parseRecord import ParseGroupedRecordCounts
from gallicaGetter.parse.parseRecord import ParseOccurrenceRecords
from gallicaGetter.parse.parseRecord import ParsePaperRecords
from gallicaGetter.parse.parseRecord import ParseContentRecord
from gallicaGetter.parse.parseRecord import build_parser


class TestParseRecord(TestCase):

    def setUp(self) -> None:
        self.parsers = [
            ParseArkRecord(),
            ParseOccurrenceRecords(requestID=1, ticketID=1),
            ParsePaperRecords(),
            ParseContentRecord(),
            ParseGroupedRecordCounts(requestID=1, ticketID=1),
        ]

    def test_build(self):
        self.assertIsInstance(build_parser('ark'), ParseArkRecord)
        self.assertIsInstance(build_parser('groupedCount', requestID=1, ticketID=1), ParseGroupedRecordCounts)
        self.assertIsInstance(build_parser('occurrence', requestID=1, ticketID=1), ParseOccurrenceRecords)
        self.assertIsInstance(build_parser('paper'), ParsePaperRecords)
        self.assertIsInstance(build_parser('content'), ParseContentRecord)

    def test_responds_to_parseResponsesToRecords(self):
        [self.assertTrue(hasattr(parser, 'parse_responses_to_records')) for parser in self.parsers]


class TestParseArkRecord(unittest.TestCase):

    def setUp(self) -> None:
        self.parser = ParseArkRecord()

    def test_parseResponsesToRecords(self):
        test_result_generator = self.parser.parse_responses_to_records(
            [
                MagicMock(data='<test></test>'),
                MagicMock(data='<test></test>'),
            ]
        )
        for testResult in test_result_generator:
            self.assertIsInstance(testResult, ArkRecord)


class TestParseGroupedRecordCounts(unittest.TestCase):

    def setUp(self) -> None:
        self.testParse = ParseGroupedRecordCounts(
            parser=MagicMock(),
            ticketID='test',
            requestID='test'
        )

    def test_parse(self):
        test = self.testParse.parse_responses_to_records(
            [
                MagicMock(data='<test></test>'),
                MagicMock(data='<test></test>'),
            ]
        )
        for testResult in test:
            self.assertIsInstance(testResult, PeriodOccurrenceRecord)


class TestParseOccurrenceRecords(unittest.TestCase):

    def setUp(self) -> None:
        self.testParse = ParseOccurrenceRecords(
            requestID=1,
            ticketID=1
        )

    def test_parseResponsesToRecords(self):
        testResponses = [
            MagicMock(data='<test></test>'),
            MagicMock(data='<test></test>'),
        ]
        test_results = self.testParse.parse_responses_to_records(testResponses)
        for result in test_results:
            self.assertIsInstance(result, VolumeOccurrenceRecord)


class TestParsePaperRecords(unittest.TestCase):

    def setUp(self) -> None:
        self.testParse = ParsePaperRecords()

    def test_parseResponsesToRecords(self):
        responses = [
            MagicMock(data='<test></test>'),
            MagicMock(data='<test></test>'),
        ]

        test = self.testParse.parse_responses_to_records(responses)

        for testResult in test:
            self.assertIsInstance(testResult, PaperRecord)
