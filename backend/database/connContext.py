import psycopg2
import redis
import os


def build_db_conn():
    return Postgres()


def build_redis_conn():
    return Redis()


class Postgres:

    def __init__(self):
        if os.environ.get('DATABASE_URL'):
            self.conn = init_prod()
        else:
            self.conn = init_local()
        self.conn.set_session(autocommit=True)

    def __enter__(self):
        print("Opening connection")
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing connection")
        self.conn.close()


class Redis:

    def __init__(self):
        if os.environ.get('REDIS_URL'):
            self.conn = init_prod_redis()
        else:
            self.conn = init_local_redis()

    def __enter__(self):
        print("Opening connection")
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing connection")
        self.conn.close()


def init_local_redis():
    print("Connecting to local redis...")
    conn = redis.Redis(host='localhost', port=6379, db=0)
    return conn


def init_prod_redis():
    REDIS_URL = os.environ['REDIS_URL']
    conn = redis.Redis.from_url(REDIS_URL)
    return conn


def init_local():
    print("Connecting to local database...")
    conn = psycopg2.connect(
        host='localhost',
        database='gallicagrapher',
        user='wgleason',
        password='postgres',
    )
    return conn


def init_prod():
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL)
    return conn


