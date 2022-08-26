from requests_toolbelt import sessions
from scripts.timeoutAndRetryHTTPAdapter import TimeoutAndRetryHTTPAdapter


class GallicaSession:

    def __init__(self, url=None):
        if url is None:
            url = "https://gallica.bnf.fr/SRU"
        self.session = sessions.BaseUrlSession(url)
        adapter = TimeoutAndRetryHTTPAdapter()
        self.session.mount("https://", adapter)

    def getSession(self):
        return self.session
