import psycopg2


class DB:

    def __init__(self):
        self.conn = None
        self.initDBConnection()

    def __enter__(self):
        return self.conn

    def __exit__(self):
        self.conn.close()
        self.conn = None

    def getConn(self):
        return self.conn

    def initDBConnection(self):
        conn = psycopg2.connect(
            host="localhost",
            database="gallicagrapher",
            user="wgleason",
            password="ilike2play"
        )
        conn.set_session(autocommit=True)
        self.conn = conn
