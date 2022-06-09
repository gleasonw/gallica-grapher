from db import DB


class TopPapers:

    def __init__(self,
                 ticketID,
                 dateString,
                 continuous):

        database = DB()
        self.conn = database.getConn()
        self.ticketID = ticketID
        self.continuous = None
        self.lowYear = None
        self.highYear = None

        self.topPapers = []
        self.selectTopPapers()
        self.parseContinuous(continuous)
        self.parseDateString(dateString)

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

    def parseContinuous(self, continuous):
        if continuous == 'false':
            self.continuous = False
        else:
            self.continuous = True

    def parseDateString(self, dateString):
        dateRange = dateString.split(",")
        self.lowYear = dateRange[0]
        self.highYear = dateRange[1]
