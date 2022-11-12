from gallicaGetter.parse.date import Date
from typing import List, Tuple


def DateGrouping(startDate, endDate, grouping) -> List[Tuple]:
    """
    Build date ranges to be used in a search query.
    :param startDate: string date format YYYY-MM-DD
    :param endDate: string date format YYYY-MM-DD
    :param grouping: string in ('year', 'month', 'all')
    :return: list of tuples of date ranges
    """
    if not startDate and not endDate:
        return [(None, None)]
    startDate = Date(startDate)
    endDate = Date(endDate)
    groupings = {
        'all': makeWideGroupingsForAllSearch,
        'year': makeYearGroupings,
        'month': makeMonthGroupings
    }
    return groupings[grouping](startDate, endDate)


def makeWideGroupingsForAllSearch(startDate, endDate):
    if not startDate.getYear() or not endDate.getYear():
        markerDate = startDate if startDate.getYear() else endDate
        if markerDate.getDay():
            return [(markerDate.getDate(), None)]
        if month := markerDate.getMonth():
            return getOneMonthInterval(month, markerDate.getYear())
        return [(
            f"{markerDate.getYear()}-01-01",
            f"{int(markerDate.getYear()) + 1}-01-01"
        )]
    else:
        start = min(startDate.getDate(), endDate.getDate())
        end = max(startDate.getDate(), endDate.getDate())
        return [(start, end)]


def makeYearGroupings(startDate, endDate):
    if not startDate.getYear() or not endDate.getYear():
        markerDate = startDate if startDate.getYear() else endDate
        return [
            (f"{markerDate.getYear()}-01-01",
             f"{int(markerDate.getYear()) + 1}-01-01")
        ]
    lowEnd, highEnd = sorted([int(startDate.getYear()), int(endDate.getYear())])
    return [(f"{year}-01-01", f"{year + 1}-01-01") for year in range(lowEnd, highEnd + 1)]


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
