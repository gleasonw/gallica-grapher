from gallicaGetter.fetch.query import FullTextQuery


def build_text_queries_for_codes(endpoint, ark_codes):
    if type(ark_codes) is not list:
        ark_codes = [ark_codes]
    return [
        FullTextQuery(
            ark=code,
            endpoint=endpoint
        )
        for code in ark_codes
    ]
