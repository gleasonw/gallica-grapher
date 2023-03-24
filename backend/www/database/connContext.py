import psycopg2
import os


def build_db_conn():
    return Postgres()


class Postgres:
    def __init__(self):
        if os.environ.get("DB_URL"):
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


def init_local():
    print("Connecting to local database...")
    conn = psycopg2.connect(
        host="localhost",
        database="gallicagrapher",
        user="wgleason",
        password="postgres",
    )
    return conn


def init_prod():
    return psycopg2.connect(os.environ.get("DB_URL"))
