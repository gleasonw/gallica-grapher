class IssueQueryForNewspaperYears:

    def __init__(self, ark: str, code: str, endpoint_url: str):
        self.ark = f'ark:/12148/{code}/date'
        self.code = code
        self.endpoint_url = endpoint_url

    def getCode(self):
        return self.code

    def get_params_for_fetch(self):
        return {"ark": self.ark}

    def __repr__(self):
        return f'ArkQuery({self.ark})'
