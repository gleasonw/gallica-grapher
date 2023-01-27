from gallicaGetter.fetch.contentQuery import ContentQuery


def build_query_for_ark_and_term(endpoint_url: str, ark: str, term: str):
    return ContentQuery(ark=ark, term=term, endpoint_url=endpoint_url)
