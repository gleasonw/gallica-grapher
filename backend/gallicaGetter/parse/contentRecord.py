from typing import List, Tuple


class ContentRecord:

    def __init__(self, num_results, pages):
        self.num_results = num_results
        self.pages = pages

    def __repr__(self):
        return f"ContentRecord(num_results={self.num_results}, first page={self.pages[0]})"

    def get_pages(self) -> List[Tuple[str, str]]:
        return self.pages
