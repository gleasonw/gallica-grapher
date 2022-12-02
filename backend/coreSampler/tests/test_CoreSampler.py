from io import StringIO
from unittest import TestCase
from unittest.mock import MagicMock
import backend.coreSampler.CoreSampler as CS


class TestCoreSampler(TestCase):

    def setUp(self):
        self.get_associated_words = CS.get_associated_words
        self.get_sample_text = CS.get_sample_text
        self.get_gallica_core = CS.get_gallica_core
        CS.get_sample_text = MagicMock(return_value=StringIO(''))
        CS.get_associated_words = MagicMock(return_value={})

    def test_get_gallica_core(self):
        self.assertEqual(
            self.get_gallica_core(
                'test',
                10,
                '1900',
                '1901',
            ),
            {}
        )

    def test_get_sample_text(self):
        self.assertEqual(
            self.get_sample_text(
                'test',
                sample_size=10,
                start_date='1900',
                end_date='1901',
                api_wrapper=MagicMock(connect=MagicMock(return_value=MagicMock(
                    get_num_results_for_args=MagicMock(return_value=[(0, 10)]),
                )))
            ).read(),
            ''
        )

    def test_get_associated_words(self):
        test_para = StringIO('the quick brown fox fox the jumped alors over fox lazy neat frx neat neat')
        expected_dict = {
            'brown': 1,
            'lazy': 1,
            'jumped': 1,
            'neat': 2,
        }
        actual_dict = self.get_associated_words(test_para, 'fox', 1)

        self.assertDictEqual(expected_dict, actual_dict)

        test_para = StringIO("""« Qui connaît un nègre les connaît tous : hâbleurs par nature, puis flatteurs 
        jusqu'à la bassesse, surtout avec les nouveaux venus. Que ce soit à Saint-Louis, au Gabon ou ailleurs, 
        un blanc nouvellement arrivé est immédiatement entouré et tâté par les noirs; ils ont vite fait de trouver 
        son côté faible ; on s'empresse, on le flatte, on l'exploite. Ils se hâtent, car ils savent par expérience 
        que ceux qui se laissent le plus facilement circonvenir deviennent généralement ensuite les plus mauvais pour 
        eux. Pour un noir, le meilleur des blancs est toujours celui à qui il parle; si l'on se trouve plusieurs 
        ensemble, il sait bien reconnaître celui qui est le plus fort, ou qui a le plus d'autorité, c'est-à-dire le 
        plus d'argent. » Les deux autres voyages de M. Alfred Marche dans l'Afrique occidentale eurent pour objet, 
        ainsi que je l'ai dit, la reconnaissance du fleuve Ogôoué. Il a accompli le premier de ces voyages en 
        ccmpagnie du marquis Victor de Compiègne, mort malheureusement depuis sur cette même terre d'Afrique. La 
        Société de Géographie de France a récompensé, en 1875, ces deux explorateurs de leurs fatigues et de leurs 
        découvertes en les honorant d'une médaille d'argent. Dans son second voyage sur l'Ogôoué, M. Alfred Mrrche a 
        fait parti d l'expédition qui eut lieu, de novembre 1875 à novembre 1878, sous les auspices de MM. les 
        Ministres de l'instruction publique et de la marine et sous les ordres de M. Savorgnan de Brazza, enseigne de 
        vaisseau, auquel était adjoint M. Noël Ballay, médecin de la marine. MM. de Brazza et de Comp;ègne ayant, 
        de leur côté. fait connaître la part qui leur revenait dans ces expéditions, M. Alfred Marche s'est, 
        autant que possible, borné à parler de ce qui le concernait plus particulièrement. Cette relation, 
        pour ainsi dire complémentaire, nous fait cependant connaître cette région par d'intéressants détails.
        """)

        self.assertDictEqual(
            self.get_associated_words(test_para, "afrique", 2),
            {
                'occidentale': 1,
                'géographie': 1,
                'terre': 1,
                'alfred': 1,
                'marche': 1,
                'société': 1,
                'malheureusement': 1,
                'objet': 1
            }
        )
