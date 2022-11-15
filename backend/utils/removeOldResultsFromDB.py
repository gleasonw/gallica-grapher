from database.connContext import getConn


def removeOldResultsFromDB():
    print('Removing old results from DB...')
    conn = getConn()
    cur = conn.cursor()
    cur.execute("""
    DELETE FROM results 
    WHERE created < NOW() - INTERVAL '1 hour'
    AND requestid > 0;
    """)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    removeOldResultsFromDB()
