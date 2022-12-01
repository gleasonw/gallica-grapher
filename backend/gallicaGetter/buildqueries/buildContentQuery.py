from gallicaGetter.fetch.contentQuery import ContentQuery


def build_query_for_ark_and_term(endpoint_url, ark, term):
    return ContentQuery(
        ark=ark,
        term=term,
        endpoint=endpoint_url
    )
