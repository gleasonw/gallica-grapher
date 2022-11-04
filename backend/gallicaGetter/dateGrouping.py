from gallicaGetter.date import Date


def DateGrouping(startDate, endDate, grouping):
    if startDate is None and endDate is None:
        return [(None, None)]
    startDate = Date(startDate)
    endDate = Date(endDate)
    groupings = {
        'all': makeWideGroupingsForAllSearch,
        'year': makeYearGroupings,
        'month': makeMonthGroupings
    }
    dates = groupings[grouping](startDate, endDate)
    return dates


def makeWideGroupingsForAllSearch(startDate, endDate):
    if startDate.getDay():
        return [(startDate.getDateText(), None)]
    elif month := startDate.getMonth():
        nextYear = int(startDate.getYear()) + 1 if month == '12' else startDate.getYear()
        nextMonth = (int(month) + 1) % 12
        return [(
            f"{startDate.getYear()}-{int(startDate.getMonth()):02}-01",
            f"{nextYear}-{nextMonth:02}-01"
        )]
    else:
        if endDate.getYear():
            endBoundary = int(endDate.getYear()) + 1
        else:
            endBoundary = int(startDate.getYear()) + 1
        return [(
            f"{startDate.getYear()}-01-01",
            f"{endBoundary}-01-01"
        )]


def makeYearGroupings(startDate, endDate):
    if endDate.getYear():
        endBoundary = int(endDate.getYear()) + 1
    else:
        endBoundary = int(startDate.getYear()) + 1
    yearGroups = set()
    for year in range(int(startDate.getYear()), endBoundary):
        yearGroups.add((f"{year}-01-01", f"{year + 1}-01-01"))
    return yearGroups


def makeMonthGroupings(startDate, endDate):
    monthGroups = set()
    for year in range(int(startDate.getYear()), int(endDate.getYear()) + 1):
        for month in range(1, 13):
            if month == 12:
                monthGroups.add((f"{year}-{month:02}-02", f"{year + 1}-01-01"))
            else:
                monthGroups.add((f"{year}-{month:02}-02", f"{year}-{month + 1:02}-01"))
    return monthGroups
