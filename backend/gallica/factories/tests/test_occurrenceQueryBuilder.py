from unittest import TestCase
from unittest.mock import patch, MagicMock, call
from occurrenceQueryBuilder import OccurrenceQueryBuilder
from occurrenceQueryBuilder import CQLFactory
from cqlStringForPaperCodes import CQLStringForPaperCodes


class TestOccurrenceQueryBuilder(TestCase):

    def setUp(self) -> None:
        self.testBuilder = OccurrenceQueryBuilder()

        self.mockTicket = MagicMock(
            key='testKey',
            terms=['term1', 'term2'],
            codes=['code1', 'code2'],
            startYear='2022',
            endYear='2023'
        )

        self.testBuilder.cql = MagicMock()
        self.testBuilder.parser = MagicMock()
        self.testBuilder.builder = MagicMock()
        self.testBuilder.queryBatcher = MagicMock()
        self.testBuilder.makeIndexer = MagicMock()
        self.testBuilder.makeCQLFactory = MagicMock()

        self.productionAddQueries = self.testBuilder.addQueriesAndNumResultsToTicket
        self.productionMakeCQLForTermsAndCodes = self.testBuilder.makeBaseQueriesForTermsAndCodes
        self.productionMakeCQLOnlyTerms = self.testBuilder.makeBaseQueriesOnlyTerms

        self.testBuilder.addQueriesAndNumResultsToTicket = MagicMock()
        self.testBuilder.makeBaseQueriesForTermsAndCodes = MagicMock()
        self.testBuilder.makeBaseQueriesOnlyTerms = MagicMock()

    def test_add_queries_and_num_results_to_ticket_given_ticket_has_codes(self):
        self.productionAddQueries(self.mockTicket)

        self.testBuilder.makeIndexer.assert_called_once()
        self.testBuilder.makeCQLFactory.assert_called_once_with(
            self.mockTicket
        )
        self.testBuilder.makeBaseQueriesForTermsAndCodes.assert_called_once()
        self.testBuilder.indexer.makeQueriesIndexedOnNumResultsForBaseCQL.assert_called_once_with(
            self.testBuilder.makeBaseQueriesForTermsAndCodes.return_value
        )
        self.testBuilder.queryBatcher.assert_called_once_with(
            self.testBuilder.indexer.makeQueriesIndexedOnNumResultsForBaseCQL.return_value
        )
        self.mockTicket.setQueries.assert_called_once_with(
            self.testBuilder.queryBatcher.return_value
        )
        self.mockTicket.setEstimateNumResults.assert_called_once_with(
            self.testBuilder.indexer.totalResultsForTicket
        )

    def test_make_cql_for_terms_and_codes(self):
        self.testBuilder.ticket = self.mockTicket
        self.testBuilder.cql.buildCQLForPaperCodes.return_value = ['cql1', 'cql2']

        self.productionMakeCQLForTermsAndCodes()

        self.testBuilder.cql.buildCQLForTerm.assert_has_calls([
            call('term1'),
            call('term2')
        ])
        self.testBuilder.cql.buildCQLForPaperCodes.assert_has_calls([
            call(),
            call()
        ])
        self.testBuilder.cql.buildCQLForTerm.return_value.format.assert_has_calls([
            call(formattedCodeString='cql1'),
            call(formattedCodeString='cql2')
        ])

    def test_make_cql_only_terms(self):
        pass


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






