from unittest import TestCase
from unittest.mock import MagicMock, patch
from gallica.gallicaSession import GallicaSession
from gallica.keywordQuery import KeywordQuery
from gallica.keywordQuery import KeywordQueryAllPapers
from gallica.keywordQuery import KeywordQuerySelectPapers
import os

here = os.path.dirname(__file__)
class TestKeywordQuery(TestCase):

    def test_post_results(self):
        self.fail()

    def test_post_missing_papers(self):
        self.fail()

    def test_move_results_to_final(self):
        self.fail()

    def test_establish_year_range(self):
        self.fail()

    def test_build_query(self):
        self.fail()


class TestKeywordQueryAllPapers(TestCase):

    def test_find_num_results_for_settings(self):
        self.fail()

    def test_build_year_range_query(self):
        KeywordQueryAllPapers.fetchNumTotalResults = MagicMock(return_value=3)

        query = KeywordQueryAllPapers(
            'brazza',
            [1850,1900],
            '1234',
            progressTracker=MagicMock(),
            dbConnection=MagicMock(),
            session=MagicMock()
        )

        self.assertEqual(
            query.baseQuery,
            'dc.date >= "1850" and dc.date <= "1900" '
            'and (gallica all "brazza") '
            'and (dc.type all "fascicule") '
            'sortby dc.date/sort.ascending')

    def test_build_dateless_query(self):
        KeywordQueryAllPapers.fetchNumTotalResults = MagicMock(return_value=3)

        query = KeywordQueryAllPapers(
            'brazza',
            [],
            '1234',
            progressTracker=MagicMock(),
            dbConnection=MagicMock(),
            session=MagicMock()
        )

        self.assertEqual(
            query.baseQuery,
            '(gallica all "brazza") '
            'and (dc.type all "fascicule") '
            'sortby dc.date/sort.ascending')

    def test_fetch_num_total_results(self):

        query = KeywordQueryAllPapers(
            'brazza',
            [],
            '1234',
            progressTracker=MagicMock(),
            dbConnection=MagicMock(),
            session=GallicaSession().getSession()
        )

        self.assertEqual(query.estimateNumResults, 78514)


class TestKeywordQuerySelectPapers(TestCase):

    def buildDummyDict(self):
        with open(os.path.join(here, "data/dummy_newspaper_choice_dicts")) as f:
            dummyNewspaperChoices = f.read().splitlines()
            choiceDict = []
            for nameCode in dummyNewspaperChoices:
                nameCode = nameCode.split(',')
                choiceDict.append(
                    {'name': nameCode[0].strip(),
                     'code': nameCode[1].strip()})
            return choiceDict

    def test_build_year_range_query(self):
        KeywordQuerySelectPapers.fetchNumTotalResults = MagicMock(return_value=3)

        choiceDict = self.buildDummyDict()
        query = KeywordQuerySelectPapers(
            'brazza',
            choiceDict,
            [1850, 1900],
            '1234',
            MagicMock(),
            MagicMock(),
            MagicMock())

        self.assertEqual(
            query.baseQuery,
            'arkPress all "{newsKey}_date" '
            'and dc.date >= "1850" '
            'and dc.date <= "1900" '
            'and (gallica all "brazza") '
            'sortby dc.date/sort.ascending')

    def test_build_dateless_query(self):
        KeywordQuerySelectPapers.fetchNumTotalResults = MagicMock(return_value=3)
        choiceDict = self.buildDummyDict()

        query = KeywordQuerySelectPapers(
            'brazza',
            choiceDict,
            [],
            '1234',
            MagicMock(),
            MagicMock(),
            MagicMock())

        self.assertEqual(
            query.baseQuery,
            'arkPress all "{newsKey}_date" '
            'and (gallica all "brazza") '
            'sortby dc.date/sort.ascending')

    def test_set_num_results_for_each_paper(self):

        choiceDict = self.buildDummyDict()
        KeywordQuerySelectPapers.fetchNumberResultsInPaper = MagicMock(return_value=['a', 1])
        KeywordQuerySelectPapers.sumUpPaperResultsForTotalEstimate = MagicMock()

        query = KeywordQuerySelectPapers(
            'brazza',
            choiceDict,
            [],
            '1234',
            MagicMock(),
            MagicMock(),
            MagicMock())

        self.assertDictEqual(query.paperCodeWithNumResults, {'a': 1})

    @patch('gallica.recordBatch.RecordBatch.getNumResults', return_value=3)
    def test_fetch_number_results_in_paper(self, mock_getNumResults):

        choiceDict = self.buildDummyDict()
        KeywordQuerySelectPapers.fetchNumTotalResults = MagicMock()
        query = KeywordQuerySelectPapers(
            'brazza',
            choiceDict,
            [],
            '1234',
            MagicMock(),
            MagicMock(),
            MagicMock())

        resultTest = query.fetchNumberResultsInPaper({'code': 'a'})

        self.assertEqual(
            resultTest,
            ('a', 3))

    def test_sum_up_paper_results_for_total_estimate(self):

        choiceDict = self.buildDummyDict()
        KeywordQuerySelectPapers.fetchNumTotalResults = MagicMock()
        query = KeywordQuerySelectPapers(
            'brazza',
            choiceDict,
            [],
            '1234',
            MagicMock(),
            MagicMock(),
            MagicMock())
        query.paperCodeWithNumResults = {'a': 1, 'b': 2}
        query.sumUpPaperResultsForTotalEstimate()

        self.assertEqual(
            query.estimateNumResults,
            3)

    def test_init_batch_queries(self):

        choiceDict = self.buildDummyDict()
        KeywordQuerySelectPapers.fetchNumTotalResults = MagicMock()
        query = KeywordQuerySelectPapers(
            'brazza',
            choiceDict,
            [],
            '1234',
            MagicMock(),
            MagicMock(),
            MagicMock())
        query.paperCodeWithNumResults = {'a': 125, 'b': 256}

        query.createURLIndecesForEachPaper()

        self.assertListEqual(
            query.batchQueryStrings,
            [
                [1, 'a'], [51, 'a'], [101, 'a'],
                [1, 'b'], [51, 'b'], [101, 'b'], [151, 'b'], [201, 'b'], [251, 'b']
            ]
        )
