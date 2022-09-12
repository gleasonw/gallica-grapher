import unittest
from cqlSelectStringForPapers import CQLSelectStringForPapers


class TestCQLSelectStringForPapers(unittest.TestCase):

    def setUp(self) -> None:
        self.codes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        self.testInstance = CQLSelectStringForPapers(self.codes, numCodesPerCQL=20)

    def test_generate_paper_cql_with_max_20_codes_each(self):
        result = self.testInstance.generatePaperCQLWithMaxNUM_CODESCodesEach()
        self.assertListEqual(
            result,
            [
                'arkPress all "a_date" or arkPress all "b_date" or arkPress all "c_date" or arkPress all "d_date" or arkPress all "e_date" or arkPress all "f_date" or arkPress all "g_date" or arkPress all "h_date" or arkPress all "i_date" or arkPress all "j_date" or arkPress all "k_date" or arkPress all "l_date" or arkPress all "m_date" or arkPress all "n_date" or arkPress all "o_date" or arkPress all "p_date" or arkPress all "q_date" or arkPress all "r_date" or arkPress all "s_date" or arkPress all "t_date"',
                'arkPress all "u_date" or arkPress all "v_date" or arkPress all "w_date" or arkPress all "x_date" or arkPress all "y_date" or arkPress all "z_date"'
            ]
        )
