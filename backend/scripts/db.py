import psycopg2
import time
import os
import json


postgresConfig = open(os.path.join(os.path.dirname(__file__), '../postgresconfig.json'), 'r')
postgresConfig = json.loads(postgresConfig.read())


class DB:

    def __init__(self):
        retries = 5
        while retries > 0:
            try:
                self.conn = psycopg2.connect(
                    host=postgresConfig["host"],
                    database=postgresConfig["database"],
                    user=postgresConfig["user"],
                    password=postgresConfig["password"]
                )
                break
            except psycopg2.OperationalError:
                time.sleep(1)
                retries -= 1
                if retries == 0:
                    raise

    def getConn(self):
        return self.conn

