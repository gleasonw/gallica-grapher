from gallicaGetter.fetch.query import FullTextQuery


def build_text_queries_for_codes(props, ark_codes):
    if type(ark_codes) is not list:
        ark_codes = [ark_codes]
    return [
        FullTextQuery(
            ark=code,
            endpoint=props.endpoint_url
        )
        for code in ark_codes
    ]
