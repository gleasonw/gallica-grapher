from gallicaGetter.contentWrapper import ContentQuery

from gallicaGetter.fullTextWrapper import FullTextQuery
from gallicaGetter.issuesWrapper import IssuesQuery
from gallicaGetter.paperQuery import PaperQuery
from gallicaGetter.volumeQuery import VolumeQuery
import aiohttp
import asyncio
from dataclasses import dataclass


@dataclass
class Response:
    xml: str
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
        xml = await response.text()
        return Response(
            xml=xml,
            query=query,
            elapsed_time=0,
        )
