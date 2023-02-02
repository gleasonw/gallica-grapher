from typing import Any, Generator


class GallicaWrapper:
    """Base class for Gallica API wrappers."""

    def __init__(self, api):
        self.api = api
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

    def get_records_for_queries(
        self,
        queries,
        on_update_progress=None,
    ):
        """The core abstraction for fetching record xml from gallica and parsing it to Python objects. Called by all subclasses."""
        raw_response = self.api.get(
            queries,
            on_update_progress=on_update_progress,
        )
        return self.parse(raw_response)
