class Response:

    def __init__(self, data, query, elapsed):
        self.xml = data
        self.query = query
        self.elapsed = elapsed