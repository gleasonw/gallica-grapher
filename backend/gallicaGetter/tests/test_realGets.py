import unittest
import gallicaGetter


class TestRealGets(unittest.TestCase):

    def test_get_volume_occurrences(self):
        getter = gallicaGetter.connect('volume')
        records = getter.get('brazza', start_date='1900', end_date='1901')
        self.assertEqual(
            len(records),
            693
        )
        
    def test_get_volume_occurrences_multi_word_term(self):
        getter = gallicaGetter.connect('volume')
        records = getter.get('organisation armée secrète', start_date='1900', end_date='2000')
        self.assertEqual(
            len(records),
            108
        )

    def test_get_period_occurrences(self):
        getter = gallicaGetter.connect('period')
        records = getter.get('brazza', start_date='1900', end_date='1901')
        self.assertEqual(
            len(records),
            2
        )
        self.assertEqual(
            records[0].count,
            691
        )

    def test_get_issues(self):
        getter = gallicaGetter.connect('issues')
        records = getter.get('cb344484501')
        self.assertEqual(
            len(records),
            1
        )
        self.assertEqual(
            records[0].years,
            [str(i) for i in range(1826, 1835)]
        )

    def test_get_content(self):
        getter = gallicaGetter.connect('content')
        records = getter.get('bpt6k267221f', 'erratum')
        self.assertEqual(
            len(records),
            1
        )
        self.assertEqual(
            int(records[0].num_results),
            1
        )

    def test_get_papers_wrapper(self):
        getter = gallicaGetter.connect('papers')
        paper = getter.get('cb32895690j')
        self.assertEqual(
            len(paper),
            1
        )
        record = paper[0]
        self.assertEqual(
            record.code,
            'cb32895690j'
        )
        self.assertEqual(
            record.publishing_years,
            [str(i) for i in range(1863, 1945)]
        )



if __name__ == '__main__':
    unittest.main()
