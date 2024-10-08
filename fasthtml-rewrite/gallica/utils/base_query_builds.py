from typing import List, Literal, Optional, Tuple
from gallica.utils.date import Date
from gallica.queries import VolumeQuery
from gallica.models import OccurrenceArgs

NUM_CODES_PER_BUNDLE = 10


def build_base_queries(
    grouping: Literal["year", "month", "all", "index_selection"],
    args: OccurrenceArgs,
) -> List[VolumeQuery]:
    """
    A factory method for VolumeQuery objects.
    Builds a list of queries to be used to fetch records from Gallica.
    If pulling all records for the query, this query will be used to get the number of records and then
    spawn additional indexed queries to fetch all records in batches of 50.
    """
    base_queries = []
    link = None
    if args.link_term and args.link_distance:
        link = (args.link_term, args.link_distance)
    for start, end in build_date_grouping(args.start_date, args.end_date, grouping):
        for code_bundle in bundle_codes(args.codes):
            if type(args.start_index) is int:
                cursor = [args.start_index]
            else:
                cursor = args.start_index
            for c in cursor:
                base_queries.append(
                    VolumeQuery(
                        terms=args.terms,
                        codes=code_bundle,
                        start_date=start,
                        end_date=end,
                        start_index=c,
                        limit=args.limit or 1,
                        link=link,
                        source=args.source,
                        sort=args.sort,
                        ocrquality=args.ocrquality,
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


def build_date_grouping(
    start_date, end_date, grouping: Literal["year", "month", "all", "index_selection"]
) -> List[Tuple]:
    """
    Build date ranges to be used in a search query.
    """
    if not start_date and not end_date:
        return [(None, None)]
    start_date = Date(start_date)
    end_date = Date(end_date)
    groupings = {
        "all": make_wide_groupings_for_all_search,
        "index_selection": make_wide_groupings_for_all_search,
        "year": make_year_groupings,
        "month": make_month_groupings,
    }
    return groupings[grouping](start_date, end_date)


def make_wide_groupings_for_all_search(startDate: Date, endDate: Date):
    if not startDate.year or not endDate.year:
        markerDate = startDate if startDate.year else endDate
        if markerDate.day:
            return [(str(markerDate), None)]
        if month := markerDate.month:
            return get_one_month_interval(int(month), int(markerDate.year))
        if not markerDate.year:
            return [(None, None)]
        return [(f"{markerDate.year}-01-01", f"{int(markerDate.year) + 1}-01-01")]
    else:
        start = min(str(startDate), str(endDate))
        end = max(str(startDate), str(endDate))
        return [(start, end)]


def make_year_groupings(startDate: Date, endDate: Date):
    if not startDate.year or not endDate.year:
        markerDate = startDate if startDate.year else endDate
        return [(f"{markerDate.year}-01-01", f"{int(markerDate.year) + 1}-01-01")]
    lowEnd, highEnd = sorted([int(startDate.year), int(endDate.year)])
    return [
        (f"{year}-01-01", f"{year + 1}-01-01") for year in range(lowEnd, highEnd + 1)
    ]


def make_month_groupings(startDate: Date, endDate: Date):
    if not startDate.year or not endDate.year:
        markerDate = startDate if startDate.year else endDate
        return get_one_month_interval(int(markerDate.month), int(markerDate.year))
    monthGroups = set()
    for year in range(int(startDate.year), int(endDate.year) + 1):
        for month in range(1, 13):
            if month == 12:
                monthGroups.add((f"{year}-{month:02}-01", f"{year + 1}-01-01"))
            else:
                monthGroups.add((f"{year}-{month:02}-01", f"{year}-{month + 1:02}-01"))
    return monthGroups


def get_one_month_interval(month: int, year: int):
    if month == 1:
        return [(f"{year}-{month:02}-02", f"{year}-{month + 1:02}-01")]
    if month == 12:
        return [(f"{year}-{month:02}-01", f"{year + 1}-01-01")]
    return [(f"{year}-{month:02}-01", f"{year}-{month + 1:02}-01")]
