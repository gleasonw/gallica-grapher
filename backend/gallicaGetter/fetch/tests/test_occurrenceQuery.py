from gallicaGetter.fetch.occurrenceQuery import OccurrenceQuery
from unittest import TestCase


class TestOccurrenceQuery(TestCase):

    def setUp(self) -> None:
        self.queryWithCodes = OccurrenceQuery(
            term='test',
            codes=['test', 'neat'],
            start_index=0,
            num_records=10,
            start_date='1901',
            end_date='1902',
            endpoint_url='test',
        )
        self.queryWithoutCodes = OccurrenceQuery(
            term='test',
            start_index=0,
            num_records=10,
            start_date='1901',
            end_date='1902',
            codes=[],
            endpoint_url='test',
            link_term='test',
            link_distance=1
        )
        self.queryWithLinkTermAndDistance = OccurrenceQuery(
            term='test',
            start_index=0,
            num_records=10,
            start_date='1901',
            end_date='1902',
            link_term='test',
            link_distance=1,
            codes=[],
            endpoint_url='test'
        )

    def test_make_copy(self):
        test = self.queryWithCodes.make_copy(start_index=1, num_records=1)
        self.assertIsInstance(test, OccurrenceQuery)
        self.assertEqual(test.start_index, 1)
        self.assertEqual(test.num_records, 1)
        self.assertEqual(test.term, self.queryWithCodes.term)
        self.assertEqual(test.codes, self.queryWithCodes.codes)
        self.assertEqual(test.start_date, self.queryWithCodes.start_date)
        self.assertEqual(test.end_date, self.queryWithCodes.end_date)
        self.assertEqual(test.endpoint_url, self.queryWithCodes.endpoint_url)
        self.assertEqual(test.link_term, self.queryWithCodes.link_term)
        self.assertEqual(test.link_distance, self.queryWithCodes.link_distance)

    def test_get_fetch_params_given_codes(self):
        test = self.queryWithCodes.get_params_for_fetch()
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
        test = self.queryWithoutCodes.get_params_for_fetch()
        self.assertIsInstance(test, dict)

    def test_get_fetch_params_with_link_term_and_distance(self):
        test = self.queryWithLinkTermAndDistance.get_params_for_fetch()
        self.assertIsInstance(test, dict)
