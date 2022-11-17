class Query:

    def __init__(self, endpoint, **kwargs):
        self.endpoint_url = endpoint
        self.post_init(kwargs)

    def get_endpoint_url(self):
        return self.endpoint_url

    def get_params_for_fetch(self):
        raise NotImplementedError

    def post_init(self, kwargs):
        pass


class FullTextQuery(Query):

    def post_init(self, kwargs):
        self.ark = kwargs["ark"]

    def get_endpoint_url(self):
        return f'{self.endpoint_url}/ark:/12148/{self.ark}.texteBrut'

    def get_params_for_fetch(self):
        return {}

    def __repr__(self) -> str:
        return f'RawTextQuery({self.ark})'


class ArkQueryForNewspaperYears(Query):

    def post_init(self, kwargs):
        self.ark = f'ark:/12148/{kwargs["code"]}/date'
        self.code = kwargs['code']

    def getCode(self):
        return self.code

    def get_params_for_fetch(self):
        return {"ark": self.ark}

    def __repr__(self):
        return f'ArkQuery({self.ark})'


class ContentQuery(Query):

    def post_init(self, kwargs):
        self.ark = kwargs['ark']
        self.term = kwargs['term']

    def get_params_for_fetch(self):
        return {
            "ark": self.ark,
            "query": self.term
        }

    def __repr__(self):
        return f'OCRQuery({self.ark}, {self.term})'


class SRUQuery(Query):

    def __init__(self, **kwargs):
        self.startIndex = kwargs['startIndex']
        self.numRecords = kwargs['numRecords']
        self.cql = None
        self.codes = kwargs.get('codes')
        super().__init__(**kwargs)

    def get_params_for_fetch(self):
        base = {
            "operation": "searchRetrieve",
            "exactSearch": "True",
            "version": 1.2,
            "startRecord": self.startIndex,
            "maximumRecords": self.numRecords,
            "query": self.get_cql()
        }
        base.update(self.get_collapsing())
        return base

    def get_cql(self):
        if not self.cql:
            self.cql = self.generate_cql()
        return self.cql

    def generate_cql(self):
        raise NotImplementedError

    def build_periodical_cql(self):
        if self.codes and self.codes[0]:
            formatted_codes = [f"{code}_date" for code in self.codes]
            return 'arkPress adj "' + '" or arkPress adj "'.join(formatted_codes) + '"'
        else:
            return "dc.type all \"fascicule\" and ocr.quality all \"Texte disponible\""

    def get_collapsing(self):
        return {"collapsing": "false"}

    def get_cql_params(self):
        raise NotImplementedError(f'{self.__class__.__name__} does not implement get_cql_params()')


class OccurrenceQuery(SRUQuery):

    def post_init(self, kwargs):
        self.start_date = kwargs['startDate']
        self.end_date = kwargs['endDate']
        self.term = kwargs['term']

        self.search_meta = kwargs['searchMetaData']
        self.link_distance = self.search_meta.get('linkDistance', 10)
        self.link_term = self.search_meta.get('linkTerm')
        self.identifier = self.search_meta.get('identifier')

    def get_id(self):
        return self.identifier

    def get_cql_params(self):
        return {
            "term": self.term,
            "endDate": self.end_date,
            "startDate": self.start_date,
            "codes": self.codes,
            "searchMetaData": self.search_meta
        }

    def get_start_date(self):
        return self.start_date

    def generate_cql(self):
        cql_components = []
        (termCQL := self.build_gram_cql()) and cql_components.append(termCQL)
        (dateCQL := self.build_date_cql()) and cql_components.append(dateCQL)
        (paperCQL := self.build_periodical_cql()) and cql_components.append(paperCQL)
        return ' and '.join(cql_components)

    def build_date_cql(self):
        if self.start_date and self.end_date:
            return f'gallicapublication_date>="{self.start_date}" and gallicapublication_date<"{self.end_date}"'
        elif self.start_date:
            return f'gallicapublication_date="{self.start_date}"'
        else:
            return ''

    def build_gram_cql(self) -> str:
        if self.link_term:
            return f'text adj "{self.term}" prox/unit=word/distance={self.link_distance} "{self.link_term}"'
        elif self.term:
            return f'text adj "{self.term}"'
        else:
            return ''

    def __repr__(self):
        return f"Query({self.get_cql()})"


class PaperQuery(SRUQuery):

    def post_init(self, kwargs):
        self.codes = kwargs.get('codes') or []

    def generate_cql(self):
        return self.build_periodical_cql()

    def get_collapsing(self):
        return {"collapsing": "true"}

    def get_cql_params(self):
        return {"codes": self.codes}

    def __repr__(self):
        return f'PaperQuery({self.codes}, {self.startIndex}, {self.numRecords})'









