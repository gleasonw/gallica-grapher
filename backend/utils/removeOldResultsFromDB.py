from database.connContext import build_db_conn


def removeOldResultsFromDB():
    print("Removing old results from DB...")
    with build_db_conn() as conn:
        with conn.cursor() as curs:
            curs.execute(
                """
            DELETE FROM results 
            WHERE created < NOW() - INTERVAL '1 hour'
            AND requestid > 0;
            """
            )
            curs.execute(
                """
            DELETE FROM groupcounts
            WHERE created < NOW() - INTERVAL '1 hour'
            AND requestid > 0;
            """
            )
        conn.commit()


if __name__ == "__main__":
    removeOldResultsFromDB()
