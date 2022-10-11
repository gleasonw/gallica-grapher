from gallica.fetchComponents.query import Query, ArkQueryForNewspaperYears, PaperQuery, OCRQuery
from unittest import TestCase


class TestOCRQuery(TestCase):

    def setUp(self) -> None:
        self.ocrQuery = OCRQuery(
            paperCode='test',
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
            "dc.type all \"fascicule\" and ocrquality > \"050.00\""
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
        self.queryWithCodes = Query(
            term='test',
            codes=['test', 'neat'],
            startIndex=0,
            numRecords=10,
            collapsing=True,
            publicationStartDate='1901',
            publicationEndDate='1902',
        )
        self.queryWithoutCodes = Query(
            term='test',
            startIndex=0,
            numRecords=10,
            collapsing=True,
            publicationStartDate='1901',
            publicationEndDate='1902',
        )
        self.queryWithLinkTermAndDistance = Query(
            term='test',
            linkTerm='neat',
            linkDistance=10,
            startIndex=0,
            numRecords=10,
            collapsing=True,
            publicationStartDate='1901',
            publicationEndDate='1902',
        )

    def test_get_fetch_params_given_codes(self):
        test = self.queryWithCodes.getFetchParams()
        self.assertDictEqual(
            test,
            {
                "operation": "searchRetrieve",
                "exactSearch": "True",
                "version": 1.2,
                "startRecord": 0,
                "maximumRecords": 10,
                "collapsing": True,
                "query": '(gallica adj "test") and (gallicapublication_date>="1901" and '
                         'gallicapublication_date<="1902") and (arkPress adj "test_date" or arkPress adj "neat_date") '
                         'and (dc.type all "fascicule")',
            }
        )

    def test_get_fetch_params_without_codes(self):
        test = self.queryWithoutCodes.getFetchParams()
        self.assertDictEqual(
            test,
            {
                "operation": "searchRetrieve",
                "exactSearch": "True",
                "version": 1.2,
                "startRecord": 0,
                "maximumRecords": 10,
                "collapsing": True,
                "query": '(gallica adj "test") and (gallicapublication_date>="1901" and '
                         'gallicapublication_date<="1902") and (dc.type all "fascicule")',
            }
        )

    def test_get_fetch_params_with_link_term_and_distance(self):
        test = self.queryWithLinkTermAndDistance.getFetchParams()
        self.assertDictEqual(
            test,
            {
                "operation": "searchRetrieve",
                "exactSearch": "True",
                "version": 1.2,
                "startRecord": 0,
                "maximumRecords": 10,
                "collapsing": True,
                "query": '(text adj "test" prox/unit=word/distance=10 "neat") and (gallicapublication_date>="1901" '
                         'and gallicapublication_date<="1902") and (dc.type all "fascicule")',
            }
        )

    def test_get_essential_data_for_making_aquery(self):
        test = self.queryWithCodes.getEssentialDataForMakingAQuery()
        self.assertDictEqual(
            test,
            {
                "term": 'test',
                "codes": ['test', 'neat'],
                "publicationStartDate": '1901',
                "publicationEndDate": '1902',
                "linkTerm": None,
                "linkDistance": 0,
            }
        )