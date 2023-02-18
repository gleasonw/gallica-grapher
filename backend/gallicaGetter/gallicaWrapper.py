from dataclasses import dataclass
from typing import Any, Generator
import asyncio
import aiohttp


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
        on_update_progress=None,
    ):
        """The core abstraction for fetching record xml from gallica and parsing it to Python objects. Called by all subclasses."""

        if not self.session:
            async with aiohttp.ClientSession() as session:
                async with asyncio.Semaphore(20):
                    raw_response = await get(
                        queries,
                        session=session,
                        on_update_progress=on_update_progress,
                    )
                    return self.parse(raw_response)
        else:
            async with asyncio.Semaphore(20):
                raw_response = await get(
                    queries,
                    session=self.session,
                    on_update_progress=on_update_progress,
                )
                return self.parse(raw_response)

