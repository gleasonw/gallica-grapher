class ContentQuery:
    def __init__(self, ark: str, term: str, endpoint_url: str):
        self.ark = ark
        self.term = term
        self.endpoint_url = endpoint_url

    def get_params_for_fetch(self):
        return {"ark": self.ark, "query": self.term}

    def __repr__(self):
        return f"OCRQuery({self.ark}, {self.term})"
