from dataclasses import dataclass
from typing import Any, Generator
import asyncio
import aiohttp
from gallicaGetter.contentWrapper import ContentQuery

from gallicaGetter.fullTextWrapper import FullTextQuery
from gallicaGetter.issuesWrapper import IssuesQuery
from gallicaGetter.paperQuery import PaperQuery
from gallicaGetter.volumeQuery import VolumeQuery


class GallicaWrapper:
    """Base class for Gallica API wrappers."""

    def __init__(self):
        self.endpoint_url = self.get_endpoint_url()
        self.post_init()

    def get(self, **kwargs):
        raise NotImplementedError(
            f"get() not implemented for {self.__class__.__name__}"
        )

    def get_endpoint_url(self):
        raise NotImplementedError(
            f"get_endpoint_url() not implemented for {self.__class__.__name__}"
        )

    def parse(
        self,
        gallica_responses,
    ) -> Generator[Any, None, None]:
        raise NotImplementedError(
            f"get_parser() not implemented for {self.__class__.__name__}"
        )

    def post_init(self):
        pass

    async def get_records_for_queries(
        self,
        queries,
        on_update_progress=None,
    ):
        """The core abstraction for fetching record xml from gallica and parsing it to Python objects. Called by all subclasses."""
        raw_response = await get(
            queries,
            on_update_progress=on_update_progress,
        )
        return self.parse(raw_response)


async def get(queries, on_update_progress=None):
    if type(queries) is not list:
        queries = [queries]

    async with aiohttp.ClientSession() as session:
        async with asyncio.Semaphore(20):
            tasks = []
            for query in queries:
                tasks.append(
                    fetch_from_gallica(
                        query=query,
                        session=session,
                        on_update_progress=on_update_progress,
                    )
                )

            return await asyncio.gather(*tasks)


@dataclass
class Response:
    xml: str
    query: VolumeQuery | PaperQuery | IssuesQuery | ContentQuery | FullTextQuery
    elapsed_time: float


async def fetch_from_gallica(
    query: VolumeQuery | PaperQuery | IssuesQuery | ContentQuery | FullTextQuery,
    session: aiohttp.ClientSession,
    on_update_progress=None,
):
    async with session.get(query.endpoint_url, params=query.params) as response:
        if on_update_progress:
            on_update_progress("FETCHING")
        xml = await response.text()
        return Response(
            xml=xml,
            query=query,
            elapsed_time=0,
        )
