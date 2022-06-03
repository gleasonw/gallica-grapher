import concurrent.futures
import psycopg2

from recordBatch import PaperRecordBatch


class Newspapers:

    def __init__(self):
        self.query = ''
        self.dbConnection = None
        self.papers = []
        self.initDBConnection()

    #TODO: Closing connection?
    def initDBConnection(self):
        conn = psycopg2.connect(
            host="localhost",
            database="gallicagrapher",
            user="wgleason",
            password="ilike2play"
        )
        conn.set_session(autocommit=True)
        self.dbConnection = conn

    #This takes a while...
    def sendGallicaPapersToDB(self):
        self.query = 'dc.type all "fascicule" and ocrquality > "050.00"'
        self.beginPaperQueries()
        self.dbConnection.close()

    def beginPaperQueries(self):
        numPapers = self.getNumPapers()
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            for batch in executor.map(self.fetchBatchPapersAtIndex,
                                      range(1, numPapers, 50)):
                for paper in batch:
                    title = paper['title']
                    date = paper['date']
                    code = paper['code']
                    print(title)
                    self.addMetadataToDB(code, title, date)

    def fetchBatchPapersAtIndex(self, index):
        batch = PaperRecordBatch(self.query, startRecord=index)
        records = batch.getRecordBatch()
        return records

    def getNumPapers(self):
        self.query = 'dc.type all "fascicule" and ocrquality > "050.00"'
        tempBatch = PaperRecordBatch(self.query, numRecords=1)
        numResults = tempBatch.getNumResults()
        return numResults

    def addPaperToDBbyCode(self, code):
        metadata = self.fetchMetadataFromCode(code)
        if metadata:
            title = metadata[0]
            code = metadata[1]
            date = metadata[2]
            self.addMetadataToDB(title, code, date)
            self.dbConnection.close()
        else:
            raise FileNotFoundError

    def fetchMetadataFromCode(self, code):
        self.query = f'arkPress all "{code}_date"'
        batch = PaperRecordBatch(self.query, numRecords=1)
        result = batch.getRecordBatch()
        if result:
            record = result[0]
            title = record['title']
            code = record['code']
            date = record['date']
            return [title, code, date]
        else:
            return None

    def addMetadataToDB(self, code, title, date=None):
        with self.dbConnection.cursor() as curs:
            curs.execute(
                """
                INSERT INTO papers (title, date, code) 
                    VALUES (%s, %s, %s);
                """, (title, date, code))

    def getPapersSimilarToKeyword(self, keyword):
        with self.dbConnection.cursor() as curs:
            keyword = keyword.lower()
            curs.execute("""
                SELECT title, code
                    FROM papers 
                    WHERE LOWER(title) LIKE %(keyword)s
                    ORDER BY title LIMIT 20;
            """, {'paperNameSearchString': '%' + keyword + '%'})
            self.papers = curs.fetchall()
            return self.nameCodeDataToJSON()

    def nameCodeDataToJSON(self):
        namedPaperCodes = []
        for paperTuple in self.papers:
            paper = paperTuple[0]
            code = paperTuple[1]
            namedPair = {'paper': paper, 'code': code}
            namedPaperCodes.append(namedPair)
        return {'paperNameCodes': namedPaperCodes}


if __name__ == "__main__":
    papers = Newspapers()
    print(papers.sendGallicaPapersToDB())