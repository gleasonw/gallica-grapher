from unittest import TestCase
from unittest.mock import patch, MagicMock
from cqlFactory import CQLFactory
from cqlFactory import CQLStringForPaperCodes


class TestCQLFactory(TestCase):

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

    @patch('cqlFactory.CQLFactory.generateCQLforOptions')
    def test_buildCQLstrings(self, mock_gen):
        self.cqlStringBuilder.buildStringsForOptions(self.optionsWithSeveralPapersAndTerms)

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

    def test_generateCQLforOptions_given_many_terms_no_papers(self):
        self.cqlStringBuilder.buildCQLforTerm = MagicMock()
        self.cqlStringBuilder.buildCQLforPaperCodes = MagicMock()
        test = self.cqlStringBuilder.buildStringsForOptions(
            self.optionsWithNoPapersAndSeveralTerms
        )
        results = [yielded for yielded in test]

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], self.cqlStringBuilder.buildCQLforTerm.return_value)

    def test_generateCQLforOptions_given_many_terms_many_papers(self):
        self.cqlStringBuilder.buildCQLforTerm = MagicMock()
        self.cqlStringBuilder.buildCQLforPaperCodes = MagicMock()
        test = self.cqlStringBuilder.buildStringsForOptions(
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

    @patch('factories.cqlFactory.CQLStringForPaperCodes.build')
    def test_format_buildCQLforPaperCodes(self, mock_CQLSelectStringForPapers):
        self.cqlStringBuilder.codes = ['code1', 'code2']
        baseQuery = '({formattedCodeString})'
        mock_CQLSelectStringForPapers.return_value.cqlSelectStrings = ['(arkPress adj "code1") or (arkPress adj "code2")']

        test = self.cqlStringBuilder.buildCQLforPaperCodes(baseQuery)

        testResult = [result for result in test]
        self.assertListEqual(
            testResult,
            ['(arkPress adj "code1_date" or arkPress adj "code2_date")']
        )


class TestCQLSelectStringForPapers(TestCase):

    def setUp(self) -> None:
        self.codes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        self.testInstance = CQLStringForPaperCodes(numCodesPerCQL=20)

    def test_generate_paper_cql_with_max_20_codes_each(self):
        result = self.testInstance.build(self.codes)
        self.assertListEqual(
            result,
            [
                'arkPress all "a_date" or arkPress all "b_date" or arkPress all "c_date" or arkPress all "d_date" or arkPress all "e_date" or arkPress all "f_date" or arkPress all "g_date" or arkPress all "h_date" or arkPress all "i_date" or arkPress all "j_date" or arkPress all "k_date" or arkPress all "l_date" or arkPress all "m_date" or arkPress all "n_date" or arkPress all "o_date" or arkPress all "p_date" or arkPress all "q_date" or arkPress all "r_date" or arkPress all "s_date" or arkPress all "t_date"',
                'arkPress all "u_date" or arkPress all "v_date" or arkPress all "w_date" or arkPress all "x_date" or arkPress all "y_date" or arkPress all "z_date"'
            ]
        )





