from db import DB


class TopPapers:

    def __init__(self,
                 ticketID,
                 dateRange,
                 continuous):

        database = DB()
        self.conn = database.getConn()
        self.ticketID = ticketID
        self.continuous = self.parseContinuous(continuous)
        dateRange = dateRange.split(",")
        self.lowYear = dateRange[0]
        self.highYear = dateRange[1]

        self.topPapers = []
        self.selectTopPapers()

    def parseContinuous(self, cont):
        if cont.lower() == "true":
            return True
        else:
            return False

    def getTopPapers(self):
        return self.topPapers

    def selectTopPapers(self):
        if self.continuous:
            self.queryTopContinuousPapers()
        else:
            self.queryTopPapers()

    def queryTopPapers(self):
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

    def queryTopContinuousPapers(self):
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