from pydantic import BaseModel
from typing import List, Optional, Dict, Literal
from gallica.context import HTMLContext

from gallica.contextSnippets import ExtractRoot
from gallica.imageSnippet import ImageResponse


class Paper(BaseModel):
    code: str
    title: str
    publisher: Optional[str]


class TopCity(BaseModel):
    count: int
    city: str


class TopPaper(BaseModel):
    count: int
    paper: Paper


class TopPaperResponse(BaseModel):
    num_results: int
    original_query: str
    top_papers: List[TopPaper]


class ContextRow(BaseModel):
    pivot: str
    left_context: str
    right_context: str
    page_url: Optional[str | None] = None
    page_num: Optional[int | None] = None


class OCRPage(BaseModel):
    page_num: int
    text: str
    page_url: str


class GallicaRecordBase(BaseModel):
    paper_title: str
    paper_code: str
    ark: str
    terms: List[str]
    date: str
    url: str
    author: str


class GallicaRowContext(GallicaRecordBase):
    context: List[ContextRow]
    ocr_quality: float


class GallicaPageContext(GallicaRecordBase):
    context: HTMLContext | ExtractRoot
    ocr_quality: float


class GallicaRecordFullPageText(GallicaRecordBase):
    context: List[OCRPage]
    ocr_quality: float


class GallicaImageContext(GallicaRecordBase):
    context: List[ImageResponse]


class UserResponse(BaseModel):
    records: (
        List[GallicaRowContext]
        | List[GallicaPageContext]
        | List[GallicaRecordFullPageText | List[GallicaImageContext]]
    )
    num_results: int
    origin_urls: List[str]


class ContextSearchArgs(BaseModel):
    terms: List[str]
    codes: Optional[List[str]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    cursor: Optional[int] = 0
    limit: Optional[int] = None
    link_term: Optional[str] = None
    link_distance: Optional[int] = None
    source: Literal["book", "periodical", "all"] = "all"
    sort: Literal["date", "relevance"] = "relevance"
    ocrquality: Optional[float] = None


class OccurrenceArgs(ContextSearchArgs):
    start_index: int | List[int] = 0


class MostFrequentRecord(BaseModel):
    term: str
    count: int
