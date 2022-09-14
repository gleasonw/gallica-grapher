from unittest import TestCase
from unittest.mock import patch, MagicMock, call
from gallica.parse import Parse
import os
from lxml import etree

class TestParse(TestCase):
    
    def setUp(self) -> None:
        self.parse = Parse(
            makePaperRecord=MagicMock(),
            makeOccurrenceRecord=MagicMock(),
            xmlParser=MagicMock()
        )
        with open(os.path.join(os.path.dirname(__file__), "resources/dummyOccurrenceRecords.xml"), "rb") as f:
            self.occurrenceXML = etree.fromstring(f.read())
        with open(os.path.join(os.path.dirname(__file__), "resources/dummyPaperRecords.xml"), "rb") as f:
            self.paperXML = etree.fromstring(f.read())

    def test_papers(self):
        papers = self.parse.papers(self.paperXML)
        
        yieldedPapers = [paper for paper in papers]

        self.assertEqual(
            len(yieldedPapers),
            13
        )
        self.parse.makePaperRecord.assert_has_calls(
            [
                call(
                    self.parse.xmlParser.getPaperCode.return_value,
                    self.parse.xmlParser.getPaperTitle.return_value,
                    self.parse.xmlParser.getURL.return_value,
                    )
            ]
        )

    def test_occurrences(self):
        occurrences = self.parse.occurrences(self.occurrenceXML)
        
        yieldedOccurrences = [occurrence for occurrence in occurrences]

        self.assertEqual(
            len(yieldedOccurrences),
            6
        )
        self.parse.makeOccurrenceRecord.assert_has_calls(
            [
                call(
                    self.parse.xmlParser.getPaperCode.return_value,
                    self.parse.xmlParser.getDate.return_value,
                    self.parse.xmlParser.getURL.return_value,
                    )
            ]
        )

    def test_numRecords(self):
        self.parse.xmlParser.getNumRecords.return_value = 6
        self.assertEqual(
            self.parse.numRecords(self.occurrenceXML),
            6
        )

    def test_yearsPublished(self):
        self.parse.xmlParser.getYearsPublished.return_value = [1900, 1901]
        self.assertEqual(
            self.parse.yearsPublished(self.occurrenceXML),
            [1900, 1901]
        )

    def test_onePaperTitleFromOccurrenceBatch(self):
        self.parse.xmlParser.getPaperTitle.return_value = "Le Monde"
        self.assertEqual(
            self.parse.onePaperTitleFromOccurrenceBatch(self.occurrenceXML),
            "Le Monde"
        )

    


        
    