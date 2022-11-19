from gallicaGetter.fetch.query import ContentQuery


class ContentQueryBuilder:

    def __init__(self, props):
        self.props = props

    def build_query_for_ark_and_term(self, ark, term):
        return ContentQuery(
            ark=ark,
            term=term,
            endpoint=self.props.endpoint_url
        )
