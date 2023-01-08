class SRUQueryMixin:
    def get_params_for_fetch(self):
        base = {
            "operation": "searchRetrieve",
            "exactSearch": "True",
            "version": 1.2,
            "startRecord": self.start_index,
            "maximumRecords": self.num_records,
            "query": self.cql and self.cql or self.generate_cql(),
            "collapsing": self.collapsing and "true" or "false",
        }
        return base

    def build_periodical_cql(self):
        if self.codes and self.codes[0]:
            formatted_codes = [f"{code}_date" for code in self.codes]
            return 'arkPress adj "' + '" or arkPress adj "'.join(formatted_codes) + '"'
        else:
            return 'dc.type all "fascicule" and ocr.quality all "Texte disponible"'
