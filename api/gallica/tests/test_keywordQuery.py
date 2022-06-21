from unittest import TestCase
from unittest.mock import MagicMock, patch
from gallica.db import DB
from gallica.keywordQuery import KeywordQuery
from gallica.keywordQuery import KeywordQueryAllPapers
from gallica.keywordQuery import KeywordQuerySelectPapers
from gallica.record import KeywordRecord
from gallica.record import Record
import os

here = os.path.dirname(__file__)


class TestKeywordQuery(TestCase):

    @staticmethod
    def getMockBatchOf5KeywordRecords():
        Record.parsePaperCodeFromXML = MagicMock(return_value="123")
        Record.parseURLFromXML = MagicMock(return_value="http://example.com")
        KeywordRecord.parseDateFromXML = MagicMock()
        KeywordRecord.checkIfValid = MagicMock()

        payload = KeywordQuery(
            'term!',
            [],
            'id!',
            MagicMock,
            MagicMock,
            MagicMock
        )
        codes = ['a', 'b', 'c', 'd', 'e']
        for i in range(5):
            mockRecord = KeywordRecord([None, None, [None]])
            mockRecord.getDate = MagicMock(return_value=[1920, 10, 1])
            mockRecord.getJSTimestamp = MagicMock(return_value=1234)
            mockRecord.getUrl = MagicMock(return_value='1234.com')
            mockRecord.getPaperCode = MagicMock(return_value=codes[i])
            payload.keywordRecords.append(mockRecord)

        return payload

    def test_post_results(self):
        dbConnection = DB().getConn()
        payload = TestKeywordQuery.getMockBatchOf5KeywordRecords()
        payload.dbConnection = dbConnection
        payload.postMissingPapers = MagicMock
        payload.copyResultsToFinalTable = MagicMock

        payload.postRecordsToHoldingResultsDB()

        with dbConnection.cursor() as curs:
            curs.execute(
                """
                    WITH resultsForRequest AS (
                        DELETE FROM holdingresults
                        WHERE requestid = 'id!'
                        RETURNING identifier, year, month, day, jstime, searchterm, paperid, requestid
                    )
                    
                    SELECT * FROM resultsForRequest;
                """
                )
            postedResults = curs.fetchall()

        firstRow = postedResults[0]
        self.assertEqual(len(postedResults), 5)
        self.assertEqual(firstRow[0], "1234.com")
        self.assertEqual(firstRow[1], 1920)
        self.assertEqual(firstRow[2], 10)
        self.assertEqual(firstRow[3], 1)
        self.assertEqual(firstRow[4], 1234)
        self.assertEqual(firstRow[5], "term!")
        self.assertEqual(firstRow[6], "a")
        self.assertEqual(firstRow[7], "id!")

    def test_generate_result_CSV_stream(self):
        payload = TestKeywordQuery.getMockBatchOf5KeywordRecords()
        testStream = payload.generateResultCSVstream()
        streamRows = testStream.getvalue().split("\n")
        firstStreamRow = streamRows[0].split("|")

        self.assertEqual(len(streamRows), 6)
        self.assertEqual(firstStreamRow[0], "1234.com")
        self.assertEqual(firstStreamRow[1], '1920')
        self.assertEqual(firstStreamRow[2], '10')
        self.assertEqual(firstStreamRow[3], '1')
        self.assertEqual(firstStreamRow[4], "1234")
        self.assertEqual(firstStreamRow[5], "term!")
        self.assertEqual(firstStreamRow[6], "a")
        self.assertEqual(firstStreamRow[7], "id!")

    def test_get_missing_papers(self):
        dbConnection = DB().getConn()
        payload = TestKeywordQuery.getMockBatchOf5KeywordRecords()
        payload.dbConnection = dbConnection
        payload.copyResultsToFinalTable = MagicMock
        payload.postMissingPapers = MagicMock

        payload.postRecordsToHoldingResultsDB()
        with dbConnection.cursor() as curs:
            missing = payload.getMissingPapers(curs)
        self.assertEqual(len(missing), 5)
        self.assertListEqual(
            sorted(missing),
            [('a',), ('b',), ('c',), ('d',), ('e',)])
        with dbConnection.cursor() as curs:
            curs.execute(
                """
                DELETE FROM holdingresults WHERE requestid = 'id!';
                """
            )

    def test_move_results_to_final(self):
        dbConnection = DB().getConn()
        payload = TestKeywordQuery.getMockBatchOf5KeywordRecords()
        payload.dbConnection = dbConnection
        payload.postMissingPapers = MagicMock
        with dbConnection.cursor() as curs:
            curs.execute("INSERT INTO papers VALUES ('',1,1,true,'a');")
            curs.execute("INSERT INTO papers VALUES ('',1,1,true,'b');")
            curs.execute("INSERT INTO papers VALUES ('',1,1,true,'c');")
            curs.execute("INSERT INTO papers VALUES ('',1,1,true,'d');")
            curs.execute("INSERT INTO papers VALUES ('',1,1,true,'e');")
            noMissingPapers = payload.getMissingPapers(curs)
            self.assertCountEqual(noMissingPapers, [])

        payload.postRecordsToHoldingResultsDB()

        with dbConnection.cursor() as curs:
            curs.execute(
            """
            SELECT * 
            FROM results 
            WHERE paperid = 'a'
            OR paperid = 'b'
            OR paperid = 'c'
            OR paperid = 'd'
            OR paperid = 'e';
            """)
            added = curs.fetchall()
        self.assertEqual(len(added), 5)
        firstRow = added[0]
        self.assertEqual(len(added), 5)
        self.assertEqual(firstRow[1], "1234.com")
        self.assertEqual(firstRow[2], 1920)
        self.assertEqual(firstRow[3], 10)
        self.assertEqual(firstRow[4], 1)
        self.assertEqual(firstRow[5], 1234)
        self.assertEqual(firstRow[6], "term!")
        self.assertEqual(firstRow[7], "a")
        self.assertEqual(firstRow[8], "id!")

        with dbConnection.cursor() as curs:
            curs.execute(
                """
                DELETE FROM results 
                WHERE paperid = 'a'
                OR paperid = 'b'
                OR paperid = 'c'
                OR paperid = 'd'
                OR paperid = 'e';
                """
            )
            curs.execute(
                """
                DELETE FROM papers 
                WHERE code = 'a'
                OR code = 'b'
                OR code = 'c'
                OR code = 'd'
                OR code = 'e';
                """
            )

    def test_establish_year_range(self):
        KeywordQuery.fetchNumTotalResults = MagicMock
        noRangeQuery = KeywordQuery(
            '',
            [],
            '1234',
            MagicMock,
            MagicMock,
            MagicMock
        )
        rangeQuery = KeywordQuery(
            '',
            [1, 1],
            '1234',
            MagicMock,
            MagicMock,
            MagicMock
        )
        self.assertFalse(noRangeQuery.isYearRange)
        self.assertTrue(rangeQuery.isYearRange)

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
