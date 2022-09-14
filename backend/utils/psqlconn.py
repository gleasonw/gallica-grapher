import psycopg2
import time
import os


class PSQLconn:

    def __init__(self):
        self.conn = None

        def initLocalConn():
            self.conn = psycopg2.connect(
                host='localhost',
                database='gallicagrapher',
                user='wgleason',
                password='postgres',
            )
            self.conn.set_session(autocommit=True)

        def initHerokuConn():
            DATABASE_URL = os.environ['DATABASE_URL']
            self.conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            self.conn.set_session(autocommit=True)

        if os.environ.get('DATABASE_URL'):
            connFunction = initHerokuConn
        else:
            connFunction = initLocalConn

        retries = 5
        while retries > 0:
            try:
                connFunction()
                break
            except psycopg2.OperationalError:
                time.sleep(1)
                retries -= 1
                if retries == 0:
                    raise

    def getConn(self):
        return self.conn

