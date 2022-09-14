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
                'arkPress adj "a_date" or arkPress adj "b_date" or arkPress adj "c_date" or arkPress adj "d_date" or arkPress adj "e_date" or arkPress adj "f_date" or arkPress adj "g_date" or arkPress adj "h_date" or arkPress adj "i_date" or arkPress adj "j_date" or arkPress adj "k_date" or arkPress adj "l_date" or arkPress adj "m_date" or arkPress adj "n_date" or arkPress adj "o_date" or arkPress adj "p_date" or arkPress adj "q_date" or arkPress adj "r_date" or arkPress adj "s_date" or arkPress adj "t_date"',
                'arkPress adj "u_date" or arkPress adj "v_date" or arkPress adj "w_date" or arkPress adj "x_date" or arkPress adj "y_date" or arkPress adj "z_date"'
            ]
        )





