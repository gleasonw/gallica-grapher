from unittest import TestCase
from io import StringIO
from backend.coreSampler.CoreSampler import get_associated_words


class Test(TestCase):
    def test_get_gallica_core(self):
        self.fail()

    def test_get_sample_text(self):
        self.fail()

    def test_get_associated_words(self):
        test_sentence = StringIO('the quick brown fox fox the jumped alors over fox lazy dog')
        expected_dict = {
            'fox': 3,
            'over': 1,
        }
        actual_dict = get_associated_words(test_sentence, 'jumped', 2)

        self.assertEqual(expected_dict, actual_dict)