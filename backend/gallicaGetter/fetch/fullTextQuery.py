class FullTextQuery:
    def __init__(self, ark: str):
        self.ark = ark

    def get_params_for_fetch(self):
        return {}

    @property
    def endpoint_url(self):
        return f"https://gallica.bnf.fr/ark:/12148/{self.ark}.texteBrut"

    def __repr__(self) -> str:
        return f"RawTextQuery({self.ark})"
