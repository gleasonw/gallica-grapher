def select_papers_similar_to_keyword(keyword, conn) -> dict:
    keyword = keyword.lower()
    with conn.cursor() as curs:
        curs.execute(
            """
            SELECT title, code, startdate, enddate
                FROM papers 
                WHERE LOWER(title) LIKE %(paperNameSearchString)s
                ORDER BY title DESC LIMIT 20;
        """,
            {"paperNameSearchString": "%" + keyword + "%"},
        )
        papersSimilarToKeyword = curs.fetchall()
    return paperDataToJSON(papersSimilarToKeyword)


def get_num_papers_in_range(conn, start: int = 0, end: int = 9999) -> int:
    with conn.cursor() as curs:
        curs.execute(
            """
            SELECT COUNT(*) FROM papers
                WHERE startdate BETWEEN %s AND %s
                    OR enddate BETWEEN %s AND %s
                    OR (startdate < %s AND enddate > %s)
                ;
            """,
            (start, end, start, end, start, end),
        )
        num_papers_over_range = curs.fetchone()
        return num_papers_over_range[0]


def paperDataToJSON(similar_papers) -> dict:
    papers = []
    for paperData in similar_papers:
        title = paperData[0]
        code = paperData[1]
        startDate = paperData[2]
        endDate = paperData[3]
        paper = {
            "title": title,
            "code": code,
            "startDate": startDate,
            "endDate": endDate,
        }
        papers.append(paper)
    return {"papers": papers}
