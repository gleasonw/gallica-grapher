from unittest import TestCase
from unittest.mock import MagicMock, call
from gallica.parse import Parse
import os


class TestParse(TestCase):

    def setUp(self) -> None:
        self.parse = Parse(
            makePaperRecord=MagicMock(),
            makeOccurrenceRecord=MagicMock(),
            recordParser=MagicMock()
        )
        with open(os.path.join(os.path.dirname(__file__), "resources/dummyOccurrenceRecords.xml"), "rb") as f:
            self.occurrenceXML = f.read()
        with open(os.path.join(os.path.dirname(__file__), "resources/dummyPaperRecords.xml"), "rb") as f:
            self.paperXML = f.read()

    def test_papers(self):
        papers = self.parse.papers(self.paperXML)

        yieldedPapers = [paper for paper in papers]

        self.assertEqual(
            len(yieldedPapers),
            15
        )
        self.parse.makePaperRecord.assert_called_with(
            code=self.parse.recordDataParser.getPaperCode.return_value,
            title=self.parse.recordDataParser.getPaperTitle.return_value,
            url=self.parse.recordDataParser.getURL.return_value,
        )

    def test_occurrences(self):
        occurrences = self.parse.occurrences(self.occurrenceXML)

        yieldedOccurrences = [occurrence for occurrence in occurrences]

        self.assertEqual(
            len(yieldedOccurrences),
            6
        )
        self.parse.makeOccurrenceRecord.assert_called_with(
            paperCode=self.parse.recordDataParser.getPaperCode.return_value,
            date=self.parse.recordDataParser.getDate.return_value,
            url=self.parse.recordDataParser.getURL.return_value,
        )

    def test_numRecords(self):
        self.parse.recordDataParser.getNumRecords.return_value = 6
        self.assertEqual(
            self.parse.numRecords(self.occurrenceXML),
            6
        )

    def test_yearsPublished(self):
        self.parse.recordDataParser.getYearsPublished.return_value = [1900, 1901]
        self.assertEqual(
            self.parse.yearsPublished(self.occurrenceXML),
            [1900, 1901]
        )

    def test_onePaperTitleFromOccurrenceBatch(self):
        self.parse.recordDataParser.getPaperTitle.return_value = "Le Monde"
        self.assertEqual(
            self.parse.onePaperTitleFromOccurrenceBatch(self.occurrenceXML),
            "Le Monde"
        )
