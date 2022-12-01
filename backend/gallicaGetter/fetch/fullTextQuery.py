class FullTextQuery:

    def __init__(self, ark: str, endpoint_url: str):
        self.ark = ark
        self.endpoint_url = endpoint_url

    def get_endpoint_url(self):
        return f'{self.endpoint_url}/ark:/12148/{self.ark}.texteBrut'

    def __repr__(self) -> str:
        return f'RawTextQuery({self.ark})'
