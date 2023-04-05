import pytest
from www.pyllicaWrapper import get_gram_data

# a few basic tests
# run `python -m pytest` in the root directory of the project


def assert_float(x):
    if x != x:
        raise (ValueError("nan value in ratio"))
    assert type(x) == float
    return x


def test_pyllica_special_chars():
    res_one = get_gram_data("création")
    res_two = get_gram_data("very-weird")
    res_one["ratio"].apply(lambda x: assert_float(x))
    res_two["ratio"].apply(lambda x: assert_float(x))


def test_pyllica_multiple_words():
    res = get_gram_data("création")
    res["ratio"].apply(lambda x: assert_float(x))


def test_pyllica_spaces():
    """Test that spaces are correctly handled."""
    res = get_gram_data("création développement")
    res["ratio"].apply(lambda x: assert_float(x))


def test_pyllica_wide_range():
    """Test that a wide range of years works does not create nans."""
    res = get_gram_data("création développement", debut=1000, fin=2000)
    res["ratio"].apply(lambda x: assert_float(x))


def test_pyllica_caps():
    res = get_gram_data("Général Boulanger")
    print(res)
    assert res is not None
    res["ratio"].apply(lambda x: assert_float(x))
    # assert some gram value is not 0
    assert res["ratio"].sum() > 0

