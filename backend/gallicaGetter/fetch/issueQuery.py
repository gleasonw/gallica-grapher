class IssueQueryForNewspaperYears:

    def __init__(self, code: str, endpoint_url: str):
        self.code = code
        self.endpoint_url = endpoint_url

    def get_code(self):
        return self.code

    def get_params_for_fetch(self):
        return {"ark": f'ark:/12148/{self.code}/date'}

    def __repr__(self):
        return f'ArkQuery({self.code})'
