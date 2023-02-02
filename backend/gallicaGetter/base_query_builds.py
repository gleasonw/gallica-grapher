from typing import List, Literal, Optional, Tuple
from gallicaGetter.date import Date
from gallicaGetter.volumeQuery import VolumeQuery

NUM_CODES_PER_BUNDLE = 10


def build_base_queries(
    terms: List[str],
    endpoint_url: str,
    grouping: str,
    link: Optional[Tuple[str, int]] = None,
    source: Optional[Literal["book", "periodical", "all"]] = None,
    sort: Optional[Literal["date", "relevance"]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    codes: Optional[List[str]] = None,
    limit: Optional[int] = None,
    cursor: int | List[int] = 0,
) -> List[VolumeQuery]:
    """
    A factory method for VolumeQuery objects.
    Builds a list of queries to be used to fetch records from Gallica.
    If pulling all records for the query, this query will be used to get the number of records and then
    spawn additional indexed queries to fetch all records in batches of 50.
    """
    base_queries = []
    for term in terms:
        for start, end in build_date_grouping(start_date, end_date, grouping):
            for code_bundle in bundle_codes(codes):
                if type(cursor) is int:
                    cursor = [cursor]
                for c in cursor:  # type: ignore
                    base_queries.append(
                        VolumeQuery(
                            term=term,
                            codes=code_bundle,
                            start_date=start,
                            end_date=end,
                            endpoint_url=endpoint_url,
                            start_index=c,
                            limit=limit or 1,
                            link=link,
                            source=source,
                            sort=sort,
                        )
                    )
    return base_queries


def bundle_codes(codes: Optional[List[str]]) -> List[List[str]]:
    if codes is None or len(codes) == 0:
        return [[]]
    return [
        codes[i : i + NUM_CODES_PER_BUNDLE]
        for i in range(0, len(codes), NUM_CODES_PER_BUNDLE)
    ]


def build_date_grouping(start_date, end_date, grouping) -> List[Tuple]:
    """
    Build date ranges to be used in a search query.
    :param start_date: string date format YYYY-MM-DD
    :param end_date: string date format YYYY-MM-DD
    :param grouping: string in ('year', 'month', 'all')
    :return: list of tuples of date ranges
    """
    if not start_date and not end_date:
        return [(None, None)]
    start_date = Date(start_date)
    end_date = Date(end_date)
    groupings = {
        "all": make_wide_groupings_for_all_search,
        "index_selection": make_wide_groupings_for_all_search,
        "year": makeYearGroupings,
        "month": makeMonthGroupings,
    }
    return groupings[grouping](start_date, end_date)


def make_wide_groupings_for_all_search(startDate, endDate):
    if not startDate.getYear() or not endDate.getYear():
        markerDate = startDate if startDate.getYear() else endDate
        if markerDate.getDay():
            return [(markerDate.getDate(), None)]
        if month := markerDate.getMonth():
            return getOneMonthInterval(month, markerDate.getYear())
        return [
            (f"{markerDate.getYear()}-01-01", f"{int(markerDate.getYear()) + 1}-01-01")
        ]
    else:
        start = min(startDate.getDate(), endDate.getDate())
        end = max(startDate.getDate(), endDate.getDate())
        return [(start, end)]


def makeYearGroupings(startDate, endDate):
    if not startDate.getYear() or not endDate.getYear():
        markerDate = startDate if startDate.getYear() else endDate
        return [
            (f"{markerDate.getYear()}-01-01", f"{int(markerDate.getYear()) + 1}-01-01")
        ]
    lowEnd, highEnd = sorted([int(startDate.getYear()), int(endDate.getYear())])
    return [
        (f"{year}-01-01", f"{year + 1}-01-01") for year in range(lowEnd, highEnd + 1)
    ]


def makeMonthGroupings(startDate, endDate):
    if not startDate.getYear() or not endDate.getYear():
        markerDate = startDate if startDate.getYear() else endDate
        return getOneMonthInterval(markerDate.getMonth(), markerDate.getYear())
    monthGroups = set()
    for year in range(int(startDate.getYear()), int(endDate.getYear()) + 1):
        for month in range(1, 13):
            if month == 12:
                monthGroups.add((f"{year}-{month:02}-02", f"{year + 1}-01-01"))
            else:
                monthGroups.add((f"{year}-{month:02}-02", f"{year}-{month + 1:02}-01"))
    return monthGroups


def getOneMonthInterval(month, year):
    month, year = int(month), int(year)
    if month == 12:
        return [(f"{year}-{month:02}-02", f"{year + 1}-01-01")]
    return [(f"{year}-{month:02}-02", f"{year}-{month + 1:02}-01")]
