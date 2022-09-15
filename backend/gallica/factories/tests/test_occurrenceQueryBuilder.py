from unittest import TestCase
from unittest.mock import patch, MagicMock
from occurrenceQueryFactory import OccurrenceQueryFactory


class TestOccurrenceQueryBuilder(TestCase):

    def setUp(self) -> None:
        self.testFactory = OccurrenceQueryFactory()

        self.testFactory.cql = MagicMock()
        self.testFactory.parser = MagicMock()
        self.testFactory.builder = MagicMock()
        self.testFactory.queryBatcher = MagicMock()

    def test_build_queries_for_options(self):
        options = {'yada yada'}

        test = self.testFactory.setQueriesAndNumResultsForTicket(options)

        self.testFactory.cql.buildStringsForTicket.assert_called_once_with(options)
        self.testFactory.builder.addQueriesAndNumResultsToTicket.assert_called_once_with(
            self.testFactory.cql.buildStringsForTicket.return_value
        )
        self.assertDictEqual(
            test,
            {
                'queries': self.testFactory.queryBatcher.return_value,
                'estimateNumResults': self.testFactory.builder.totalResultsForTicket
            }
        )

from unittest import TestCase
from unittest.mock import patch, MagicMock
from cqlFactory import CQLFactory
from cqlFactory import CQLStringForPaperCodes


class TestCQLFactory(TestCase):

    def setUp(self) -> None:
        self.cqlStringBuilder = CQLFactory()

        self.buildStringsForTicket = self.cqlStringBuilder.buildStringsForTicket
        self.cqlStringBuilder.buildStringsForTicket = MagicMock()

        self.generateCQLforCodesAndTerms = self.cqlStringBuilder.generateCQLforCodesAndTerms
        self.cqlStringBuilder.generateCQLforCodesAndTerms = MagicMock()

        self.generateCQLforTerms = self.cqlStringBuilder.generateCQLforTerms
        self.cqlStringBuilder.generateCQLforTerms = MagicMock()

        self.buildCQLforTerm = self.cqlStringBuilder.buildCQLforTerm
        self.cqlStringBuilder.buildCQLforTerm = MagicMock()

        self.buildCQLforPaperCodes = self.cqlStringBuilder.buildCQLforPaperCodes
        self.cqlStringBuilder.buildCQLforPaperCodes = MagicMock()

        self.ticketWithSeveralPapersAndTerms = MagicMock(
            startYear='1900',
            endYear='1901',
            codes=['code1', 'code2'],
            terms=['term1', 'term2']
        )

        self.ticketWithNoPapersAndSeveralTerms = MagicMock(
            startYear='1900',
            endYear='1901',
            codes=[],
            terms=['term1', 'term2']
        )

        self.ticketWithNoPapersAndOneTerm = MagicMock(
            startYear='1900',
            endYear='1901',
            codes=[],
            terms=['term1']
        )

        self.ticketWithOnePaperAndOneTerm = MagicMock(
            startYear='1900',
            endYear='1901',
            codes=['code1'],
            terms=['term1']
        )

    def test_buildCQLstrings(self):
        self.buildStringsForTicket(self.ticketWithSeveralPapersAndTerms)

        self.assertEqual(
            self.cqlStringBuilder.ticket.startYear,
            self.ticketWithSeveralPapersAndTerms.startYear
        )
        self.assertEqual(
            self.cqlStringBuilder.ticket.endYear,
            self.ticketWithSeveralPapersAndTerms.endYear
        )
        self.assertEqual(
            self.cqlStringBuilder.ticket.terms,
            self.ticketWithSeveralPapersAndTerms.terms
        )
        self.assertListEqual(
            self.cqlStringBuilder.ticket.codes,
            ['code1', 'code2']
        )
        self.cqlStringBuilder.generateCQLforCodesAndTerms.assert_called_once()

    def test_generate_cql_for_codes_and_terms(self):
        self.cqlStringBuilder.ticket = self.ticketWithSeveralPapersAndTerms
        self.cqlStringBuilder.buildCQLforTerm.side_effect = lambda x: x

        test = self.generateCQLforCodesAndTerms()

        self.assertEqual(len(test), 2)
        self.assertEqual(
            test['term1'
            ]
        )

    def test_generateCQLforOptions_given_many_terms_many_papers(self):
        self.cqlStringBuilder.buildCQLforTerm = MagicMock()
        self.cqlStringBuilder.buildCQLforPaperCodes = MagicMock()
        test = self.cqlStringBuilder.buildStringsForTicket(
            self.ticketWithSeveralPapersAndTerms
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

    @patch('factories.cql.CQLStringForPaperCodes.build')
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






