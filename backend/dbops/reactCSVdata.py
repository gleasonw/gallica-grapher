from psqlconn import PSQLconn


class ReactCSVdata:

    def __init__(self):
        self.conn = PSQLconn().getConn()
        self.csvData = None

    def getCSVData(self, ticketIDs):
        tupledTickets = tuple(ticketIDs.split(','))
        with self.conn.cursor() as cur:
            cur.execute("""
            SELECT searchterm, identifier, year, month, day 
            FROM results 
            WHERE ticketid IN %s
            ORDER BY year, month, day
            """, (tupledTickets,))
            self.csvData = cur.fetchall()
        rowLabels = ['ngram', 'identifier', 'year', 'month', 'day']
        self.csvData.insert(0, rowLabels)
        return self.csvData

