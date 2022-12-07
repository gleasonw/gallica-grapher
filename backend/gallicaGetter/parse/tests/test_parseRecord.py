import unittest
from unittest import TestCase
from unittest.mock import MagicMock
import gallicaGetter.parse.issueYearRecord as issues
import gallicaGetter.parse.periodRecords as periodRecords
import gallicaGetter.parse.volumeRecords as volumeRecords
import gallicaGetter.parse.paperRecords as paperRecords


class TestParseArkRecord(unittest.TestCase):

    def test_parseResponsesToRecords(self):
        test_result_generator = issues.parse_responses_to_records(
            [
                MagicMock(xml='<test></test>'),
                MagicMock(xml='<test></test>'),
            ]
        )
        for testResult in test_result_generator:
            self.assertIsInstance(testResult, issues.IssueYearRecord)


class TestParseGroupedRecordCounts(unittest.TestCase):

    def test_parse(self):
        test = periodRecords.parse_responses_to_records(
            [
                MagicMock(xml='<test></test>'),
                MagicMock(xml='<test></test>'),
            ]
        )
        for testResult in test:
            self.assertIsInstance(testResult, periodRecords.PeriodRecord)


class TestParseOccurrenceRecords(unittest.TestCase):

    def test_parseResponsesToRecords(self):
        testResponses = [
            MagicMock(xml='<test></test>'),
            MagicMock(xml='<test></test>'),
        ]
        test_results = volumeRecords.parse_responses_to_records(testResponses)
        for result in test_results:
            self.assertIsInstance(result, volumeRecords.VolumeRecord)


class TestParsePaperRecords(unittest.TestCase):

    def test_parseResponsesToRecords(self):
        responses = [
            MagicMock(xml='<test></test>'),
            MagicMock(xml='<test></test>'),
        ]

        test = paperRecords.parse_responses_to_records(responses)

        for testResult in test:
            self.assertIsInstance(testResult, paperRecords.PaperRecord)
