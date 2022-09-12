from unittest import TestCase
from unittest.mock import patch
from cqlFactory import CQLFactory


class TestCQLforTicket(TestCase):

    def setUp(self) -> None:
        self.cqlStringBuilder = CQLFactory()
        self.optionsWithSeveralPapersAndTerms = {
            'startYear': '1900',
            'endYear': '1901',
            'terms': ['term1', 'term2'],
            'papersAndCodes': [
                {
                    'code': 'code1',
                    'paper': 'paper1'
                },
                {
                    'code': 'code2',
                    'paper': 'paper2'
                }
            ]
        }

        self.optionsWithNoPapersAndSeveralTerms = {
            'startYear': '1900',
            'endYear': '1901',
            'terms': ['term1', 'term2'],
            'papersAndCodes': []
        }

        self.optionsWithNoPapersAndOneTerm = {
            'startYear': '1900',
            'endYear': '1901',
            'terms': ['term1'],
            'papersAndCodes': []
        }

        self.optionsWithOnePaperAndOneTerm = {
            'startYear': '1900',
            'endYear': '1901',
            'terms': ['term1'],
            'papersAndCodes': [{
                'code': 'code1',
                'paper': 'paper1'
            }]
        }

    @patch('gallica.cqlforticket.CQLforTicket.generateCQLforOptions')
    def test_buildCQLstrings(self, mock_gen):
        self.cqlStringBuilder.buildCQLstrings(self.optionsWithSeveralPapersAndTerms)

        self.assertEqual(
            self.cqlStringBuilder.startYear,
            self.optionsWithSeveralPapersAndTerms['startYear']
        )
        self.assertEqual(
            self.cqlStringBuilder.endYear,
            self.optionsWithSeveralPapersAndTerms['endYear']
        )
        self.assertEqual(
            self.cqlStringBuilder.terms,
            self.optionsWithSeveralPapersAndTerms['terms']
        )
        self.assertListEqual(
            self.cqlStringBuilder.codes,
            ['code1', 'code2']
        )
        mock_gen.assert_called_once()

    @patch('gallica.cqlforticket.CQLforTicket.buildCQLforTerm')
    @patch('gallica.cqlforticket.CQLforTicket.buildCQLforPaperCodes')
    def test_generateCQLforOptions_given_many_terms_no_papers(self, mock_buildCQLforPaperCodes, mock_buildCQLforTerm):
        test = self.cqlStringBuilder.buildCQLstrings(
            self.optionsWithNoPapersAndSeveralTerms
        )
        results = [yielded for yielded in test]

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], mock_buildCQLforTerm.return_value)

    @patch('gallica.cqlforticket.CQLforTicket.buildCQLforTerm')
    @patch('gallica.cqlforticket.CQLforTicket.buildCQLforPaperCodes')
    def test_generateCQLforOptions_given_many_terms_many_papers(self, mock_buildCQLforPaperCodes, mock_buildCQLforTerm):
        test = self.cqlStringBuilder.buildCQLstrings(
            self.optionsWithSeveralPapersAndTerms
        )

        self.assertIsInstance(test, type((yielded for yielded in test)))

    def test_buildCQLforTerm_no_papers(self):
        self.cqlStringBuilder.startYear = '1900'
        self.cqlStringBuilder.endYear = '1901'
        self.cqlStringBuilder.codes = []

        test = self.cqlStringBuilder.buildCQLforTerm('term1')

        self.assertEqual(
            test,
            'dc.date >= "1900" and dc.date <= "1901" and (gallica adj "term1") and (dc.type adj "fascicule") sortby dc.date/sort.ascending'
        )

    def test_buildCQLforTerm_with_papers(self):
        self.cqlStringBuilder.startYear = '1900'
        self.cqlStringBuilder.endYear = '1901'
        self.cqlStringBuilder.codes = ['code1', 'code2']

        test = self.cqlStringBuilder.buildCQLforTerm('term1')

        self.assertEqual(
            test,
            '({formattedCodeString}) and dc.date >= "1900" and dc.date <= "1901" and (gallica adj "term1") and (dc.type adj "fascicule") sortby dc.date/sort.ascending'
        )

    @patch('gallica.cqlforticket.CQLSelectStringForPapers')
    def test_format_buildCQLforPaperCodes(self, mock_CQLSelectStringForPapers):
        self.cqlStringBuilder.codes = ['code1', 'code2']
        baseQuery = '({formattedCodeString})'
        mock_CQLSelectStringForPapers.return_value.cqlSelectStrings = ['(arkPress adj "code1") or (arkPress adj "code2")']

        test = self.cqlStringBuilder.buildCQLforPaperCodes(baseQuery)

        testResult = [result for result in test]
        self.assertListEqual(
            testResult,
            ['((arkPress adj "code1") or (arkPress adj "code2"))']
        )




