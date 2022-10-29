import psycopg2
import os


class PSQLconn:

    _savedConn = None

    def __new__(cls):
        if cls._savedConn is None:
            cls._savedConn = super().__new__(cls)
        else:
            conn = cls._savedConn.getConn()
            if conn.closed:
                cls._savedConn = super().__new__(cls)
        return cls._savedConn

    def __init__(self):
        self.conn = None
        if os.environ.get('DATABASE_URL'):
            self.initHerokuConn()
        else:
            self.initLocalConn()

    def getConn(self):
        return self.conn

    def initLocalConn(self):
        self.conn = psycopg2.connect(
            host='localhost',
            database='gallicagrapher',
            user='wgleason',
            password='postgres',
        )
        self.conn.set_session(autocommit=True)

    def initHerokuConn(self):
        DATABASE_URL = os.environ['DATABASE_URL']
        self.conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        self.conn.set_session(autocommit=True)

