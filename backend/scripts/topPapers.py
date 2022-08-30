from psqlconn import PSQLconn


class TopPapers:

    def __init__(
            self,
            ticketID,
            continuous,
            dateRange=None):

        self.conn = PSQLconn().getConn()
        self.ticketID = ticketID
        self.continuous = continuous.lower() == "true"
        if self.continuous:
            self.lowYear, self.highYear = dateRange.split(",")
        self.topPapers = []

    def getTopPapers(self):
        if self.continuous:
            self.selectTopContinuousPapers()
        else:
            self.selectTopPapers()
        return self.topPapers

    def selectTopPapers(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
    
            SELECT papers.title, count(paperid) AS papercount
                FROM (SELECT paperid 
                        FROM results WHERE requestid = %s) 
                        AS ticket
                INNER JOIN papers ON ticket.paperid = papers.code 
                GROUP BY papers.title
                ORDER BY papercount DESC
                LIMIT 10;
    
            """, (self.ticketID,))
            self.topPapers = cursor.fetchall()

    def selectTopContinuousPapers(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""

            SELECT continuousPapersForRange.title, count(paperid) AS papercount
                FROM 
                (SELECT paperid FROM results 
                    WHERE 
                        requestid = %s)
                AS ticket
                INNER JOIN 
                (SELECT code, title FROM papers 
                    WHERE 
                        papers.startdate < %s AND papers.enddate > %s
                            AND
                        continuous IS TRUE) 
                AS continuousPapersForRange
                ON ticket.paperid = continuousPapersForRange.code 
                GROUP BY continuousPapersForRange.title
                ORDER BY papercount DESC
                LIMIT 10;

            """, (self.ticketID, self.lowYear, self.highYear,))
            self.topPapers = cursor.fetchall()
