from utils.psqlconn import PSQLconn


class RecordDataForUser:

    ticketResultsWithPaperName = """
    SELECT searchterm, title, year, month, day, identifier
    FROM results
    JOIN papers
    ON results.paperid = papers.code
    WHERE ticketid in %s
    AND requestid = %s
    """

    def __init__(self):
        self.conn = PSQLconn().getConn()
        self.csvData = None

    #TODO: compress csv before returning to user
    def getCSVData(self, ticketIDs, requestID):
        tupledTickets = tuple(ticketIDs.split(','))
        with self.conn.cursor() as cur:
            cur.execute(f"""
            {self.ticketResultsWithPaperName}
            ORDER BY year, month, day
            """, (tupledTickets,requestID))
            self.csvData = cur.fetchall()
        rowLabels = ['ngram', 'identifier', 'periodical', 'year', 'month', 'day']
        self.csvData.insert(0, rowLabels)
        return self.csvData

    def getRecordsForDisplay(self, ticketIDs, requestID, year, month, day, limit, offset):
        if year and month and day:
            return self.getYearMonthDayRecordsForDisplay(ticketIDs, requestID, year, month, day, limit, offset)
        elif year and month:
            return self.getYearMonthRecordsForDisplay(ticketIDs, requestID, year, month, limit, offset)
        elif year:
            return self.getYearRecordsForDisplay(ticketIDs, requestID, year, limit, offset)
        else:
            return []

    def getYearRecordsForDisplay(self, ticketIDs, requestID, year, limit, offset):
        tupledTickets = tuple(ticketIDs.split(','))
        with self.conn.cursor() as cur:
            cur.execute(f"""
            {self.ticketResultsWithPaperName}
            AND year = %s
            ORDER BY year, month, day
            LIMIT %s
            OFFSET %s
            ; 
            """, (tupledTickets, requestID, year, limit, offset))
            return cur.fetchall()

    def getYearMonthRecordsForDisplay(self, ticketIDs, requestID, year, month, limit, offset):
        tupledTickets = tuple(ticketIDs.split(','))
        with self.conn.cursor() as cur:
            cur.execute(f"""
            {self.ticketResultsWithPaperName}
            AND year = %s 
            AND month = %s
            ORDER BY year, month, day
            LIMIT %s
            OFFSET %s
            """, (tupledTickets, requestID, year, month, limit, offset))
            return cur.fetchall()

    def getYearMonthDayRecordsForDisplay(self, ticketIDs, requestID, year, month, day, limit, offset):
        tupledTickets = tuple(ticketIDs.split(','))
        with self.conn.cursor() as cur:
            cur.execute(f"""
            {self.ticketResultsWithPaperName}
            AND year = %s 
            AND month = %s
            AND day = %s
            ORDER BY year, month, day
            LIMIT %s
            OFFSET %s
            """, (tupledTickets, requestID, year, month, day, limit, offset))
            return cur.fetchall()

    def clearUserRecordsAfterCancel(self, requestID):
        with self.conn.cursor() as cur:
            cur.execute("""
            DELETE FROM results
            WHERE requestid = %s
            """, (requestID,))
            self.conn.commit()


