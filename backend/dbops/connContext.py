import psycopg2
import os


def buildDBConn():
    if os.environ.get('DATABASE_URL'):
        conn = initHerokuConn()
    else:
        conn = initLocalConn()
    conn.set_session(autocommit=True)
    return conn


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
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn


_conn = buildDBConn()


def getConn():
    global _conn
    if _conn.closed:
        _conn = buildDBConn()
    return _conn
