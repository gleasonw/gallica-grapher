import psycopg2
import os

_conn = None


def buildDBConn():
    global _conn
    if os.environ.get('DATABASE_URL'):
        _conn = initHerokuConn()
    else:
        _conn = initLocalConn()
    _conn.set_session(autocommit=True)


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
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn


def getConn():
    global _conn
    if _conn is None or _conn.closed:
        buildDBConn()
    return _conn
