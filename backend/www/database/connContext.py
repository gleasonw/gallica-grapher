import os
import MySQLdb
import dotenv

dotenv.load_dotenv()


def build_db_conn():
    return MySQL()


class MySQL:
    def __init__(self):
        print("Opening connection")
        self.conn = MySQLdb.connect(
            host=os.environ.get("HOST"),
            user=os.environ.get("DB_USER"),
            passwd=os.environ.get("PASSWORD"),
            db=os.environ.get("DATABASE"),
            ssl_mode="VERIFY_IDENTITY",
            ssl={"ca": "/etc/ssl/certs/ca-certificates.crt"},
        )

    def __enter__(self):
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing connection")
        self.conn.commit()
        self.conn.close()
