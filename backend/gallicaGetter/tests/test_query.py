from query import OccurrenceQuery, ArkQueryForNewspaperYears, PaperQuery, ContentQuery
from unittest import TestCase


class TestOCRQuery(TestCase):

    def setUp(self) -> None:
        self.ocrQuery = ContentQuery(
            ark='test',
            term='test'
        )

    def test_get_fetch_params(self):
        test = self.ocrQuery.getFetchParams()

        self.assertDictEqual(
            test,
            {
                "ark": 'test',
                "query": 'test'
            }
        )


class TestPaperQuery(TestCase):

    def setUp(self) -> None:
        self.paperQuery = PaperQuery(
            startIndex=0,
            numRecords=10,
        )

    def test_get_cql_all_papers(self):
        test = self.paperQuery.getCQL()
        self.assertEqual(
            test,
            "dc.type all \"fascicule\" and ocr.quality all \"Texte disponible\""
        )


class TestArkQueryForNewspaperYears(TestCase):

    def setUp(self) -> None:
        self.arkQuery = ArkQueryForNewspaperYears(
            code='test'
        )

    def test_get_fetch_params(self):
        test = self.arkQuery.getFetchParams()
        self.assertDictEqual(
            test,
            {'ark': 'ark:/12148/test/date'}
        )


class TestQuery(TestCase):

    def setUp(self) -> None:
        self.queryWithCodes = OccurrenceQuery(
            term='test',
            codes=['test', 'neat'],
            startIndex=0,
            numRecords=10,
            collapsing=True,
            startDate='1901',
            endDate='1902',
            searchMetaData={
                'linkDistance': 0,
                'linkTerm': ''
            },
        )
        self.queryWithoutCodes = OccurrenceQuery(
            term='test',
            startIndex=0,
            numRecords=10,
            collapsing=True,
            startDate='1901',
            endDate='1902',
            searchMetaData={
                'linkDistance': 0,
                'linkTerm': ''
            },
            codes=[]
        )
        self.queryWithLinkTermAndDistance = OccurrenceQuery(
            term='test',
            startIndex=0,
            numRecords=10,
            collapsing=True,
            startDate='1901',
            endDate='1902',
            searchMetaData={
                'linkDistance': 0,
                'linkTerm': ''
            },
            codes=[]
        )

    def test_get_fetch_params_given_codes(self):
        test = self.queryWithCodes.getFetchParams()
        self.assertDictEqual(
            test,
            {
                "operation": "searchRetrieve",
                "version": 1.2,
                "exactSearch": "True",
                "startRecord": 0,
                "maximumRecords": 10,
                "collapsing": 'false',
                "query": 'text adj "test" and gallicapublication_date>="1901" and gallicapublication_date<"1902" and arkPress adj "test_date" or arkPress adj "neat_date"'
            }
        )

    def test_get_fetch_params_without_codes(self):
        test = self.queryWithoutCodes.getFetchParams()
        self.assertIsInstance(test, dict)

    def test_get_fetch_params_with_link_term_and_distance(self):
        test = self.queryWithLinkTermAndDistance.getFetchParams()
        self.assertIsInstance(test, dict)

    def test_get_essential_data_for_making_aquery(self):
        test = self.queryWithCodes.getEssentialDataForMakingAQuery()
        self.assertDictEqual(
            test,
            {
                'term': 'test',
                'codes': ['test', 'neat'],
                'endDate': '1902',
                'startDate': '1901',
                "searchMetaData": self.queryWithCodes.searchMetaData
            }
        )