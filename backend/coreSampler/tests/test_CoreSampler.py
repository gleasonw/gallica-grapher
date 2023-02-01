from io import StringIO
from unittest import TestCase
from unittest.mock import MagicMock
import backend.coreSampler.CoreSampler as CS


class TestCoreSampler(TestCase):
    def setUp(self):
        self.get_associated_words = CS.get_associated_words
        self.get_sample_text = CS.get_sample_text
        self.get_gallica_core = CS.get_gallica_core
        CS.get_sample_text = MagicMock(return_value=StringIO(""))
        CS.get_associated_words = MagicMock(return_value={})

    def test_get_gallica_core(self):
        self.assertEqual(
            self.get_gallica_core(
                "test",
                10,
                "1900",
                "1901",
                api_wrapper=MagicMock(),
            ),
            {},
        )

    def test_get_sample_text(self):
        self.assertEqual(
            self.get_sample_text(
                "test",
                sample_size=10,
                start_date="1900",
                end_date="1901",
                api_wrapper=MagicMock(
                    connect=MagicMock(
                        return_value=MagicMock(
                            get_num_results_for_args=MagicMock(return_value=[(0, 10)]),
                        )
                    )
                ),
            ).read(),
            "",
        )

    def test_get_associated_words(self):
        test_para = StringIO(
            "the quick brown fox fox the jumped alors over fox lazy neat frx neat neat"
        )
        expected_dict = {
            "brown": 1,
            "lazy": 1,
            "jumped": 1,
            "neat": 2,
        }
        actual_dict = self.get_associated_words(test_para, "fox", 1)

        self.assertDictEqual(expected_dict, actual_dict)

        test_para = StringIO()

        self.assertDictEqual(
            self.get_associated_words(test_para, "afrique", 2),
            {
                "occidentale": 1,
                "géographie": 1,
                "terre": 1,
                "alfred": 1,
                "marche": 1,
                "société": 1,
                "malheureusement": 1,
                "objet": 1,
            },
        )
