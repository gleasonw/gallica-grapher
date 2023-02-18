from dataclasses import dataclass
from typing import Any, Generator
import asyncio
import aiohttp

from gallicaGetter.queries import (
    ContentQuery,
    FullTextQuery,
    IssuesQuery,
    PaperQuery,
    VolumeQuery,
)


class GallicaWrapper:
    """Base class for Gallica API wrappers."""

    def __init__(self, session: aiohttp.ClientSession | None = None):
        self.endpoint_url = self.get_endpoint_url()
        self.session = session
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
        session: aiohttp.ClientSession,
        on_update_progress=None,
    ):
        """The core abstraction for fetching record xml from gallica and parsing it to Python objects. Called by all subclasses."""

        raw_response = await get(
            queries,
            session=session,
            on_update_progress=on_update_progress,
        )
        return self.parse(raw_response)


@dataclass
class Response:
    xml: bytes
    query: VolumeQuery | PaperQuery | IssuesQuery | ContentQuery | FullTextQuery
    elapsed_time: float


async def get(queries, session: aiohttp.ClientSession, on_update_progress=None):
    if type(queries) is not list:
        queries = [queries]
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


async def fetch_from_gallica(
    query: VolumeQuery | PaperQuery | IssuesQuery | ContentQuery | FullTextQuery,
    session: aiohttp.ClientSession,
    on_update_progress=None,
):
    async with session.get(query.endpoint_url, params=query.params) as response:
        if on_update_progress:
            on_update_progress("FETCHING")
        xml = await response.content.read()
        return Response(
            xml=xml,
            query=query,
            elapsed_time=0,
        )
