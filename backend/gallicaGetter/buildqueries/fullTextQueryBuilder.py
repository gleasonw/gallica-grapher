from gallicaGetter.fetch.query import FullTextQuery


class FullTextQueryBuilder:

    def __init__(self, props):
        self.props = props

    def build_queries_for_ark_codes(self, ark_codes):
        if type(ark_codes) is not list:
            ark_codes = [ark_codes]
        return [
            FullTextQuery(
                ark=code,
                endpoint=self.props.endpoint_url
            )
            for code in ark_codes
        ]
