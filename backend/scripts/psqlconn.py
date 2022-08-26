import psycopg2
import time
from settings import DATABASES


class PSQLconn:

    def __init__(self):
        retries = 5
        while retries > 0:
            try:
                self.conn = psycopg2.connect(
                    host=DATABASES['default']['HOST'],
                    database=DATABASES['default']['NAME'],
                    user=DATABASES['default']['USER'],
                    password=DATABASES['default']['PASSWORD'],
                    port=DATABASES['default']['PORT']
                )
                break
            except psycopg2.OperationalError:
                time.sleep(1)
                retries -= 1
                if retries == 0:
                    raise

    def getConn(self):
        return self.conn

