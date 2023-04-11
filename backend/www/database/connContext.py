import os
import pymysql
import dotenv

dotenv.load_dotenv()


def build_db_conn():
    return MySQL()


class MySQL:
    
    def __init__(self):
        self.conn = pymysql.connect(
            host=os.environ.get("HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("PASSWORD"),
            database=os.environ.get("DATABASE"),
            ssl={"ca": "/etc/ssl/certs/ca-certificates.crt"},
        )

    def __enter__(self):
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing connection")
        self.conn.commit()
        self.conn.close()
