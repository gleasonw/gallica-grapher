from io import StringIO
from unittest import TestCase
from unittest.mock import MagicMock
from gallicaGetter.coreSampler import get_associated_words, get_sample_text, get_gallica_core


class TestCoreSampler(TestCase):
    def setUp(self):
        self.get_gallica_core = get_gallica_core
        get_sample_text = MagicMock(return_value=StringIO(""))
        get_associated_words = MagicMock(return_value={})

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
            get_sample_text(
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
        actual_dict = get_associated_words(test_para, "fox", 1)

        self.assertDictEqual(expected_dict, actual_dict)

        test_para = StringIO(
            """
        c’est possible, venez toujours à la maison. — Père capucin, s’écriait la ménagère instruite du motif de sa visite, venez, voilà une carotte. . . mais ça ne fera pas une soupe bien riche. — Nous(...)Et le capucin s’en allait avec sa marmite garnie d’eau, d’un caillou, d’une carotte et d’un poireau(...)Une soupe où il n’y a qu’un caillou, une carotte et un poireau. .. — En effet, ça doit être pas long... ça doit pas être bon non plus. — Nous avons fait vœu d’abstinence
        
        """
        )

        self.assertDictEqual(
            get_associated_words(test_para, "caillou", 2),
            {
                "carotte": 2,
                "eau": 1,
                "garnie": 1,
                "poireau": 2,
                "soupe": 1,
            },
        )
