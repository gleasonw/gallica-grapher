from typing import List
from ..fetch.issueQuery import IssueQueryForNewspaperYears


def build_issue_queries_for_codes(
    codes, endpoint_url
) -> List[IssueQueryForNewspaperYears]:
    if type(codes) == str:
        codes = [codes]
    return [
        IssueQueryForNewspaperYears(code=code, endpoint_url=endpoint_url)
        for code in codes
    ]
