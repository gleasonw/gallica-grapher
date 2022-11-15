import psycopg2
import os


def build_db_conn():
    return ConnectionContext()


class ConnectionContext:

    def __init__(self):
        if os.environ.get('DATABASE_URL'):
            self.conn = initHerokuConn()
        else:
            self.conn = initLocalConn()
        self.conn.set_session(autocommit=True)

    def __enter__(self):
        print("Opening connection")
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing connection")
        self.conn.close()


def initLocalConn():
    print("Connecting to local database...")
    conn = psycopg2.connect(
        host='localhost',
        database='gallicagrapher',
        user='wgleason',
        password='postgres',
    )
    return conn


def initHerokuConn():
    print("Connecting to Heroku database...")
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL)
    return conn


