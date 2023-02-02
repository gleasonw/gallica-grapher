from typing import Any, Callable, Generator, Optional


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
        gallica_response,
        on_get_total_records: Optional[Callable[[int], None]] = None,
    ) -> Generator[Any, None, None]:
        raise NotImplementedError(
            f"get_parser() not implemented for {self.__class__.__name__}"
        )

    def post_init(self):
        pass

    def get_records_for_queries(
        self,
        queries,
        onUpdateProgress=None,
        on_get_total_records: Optional[Callable[[int], None]] = None,
    ):
        raw_response = self.api.get(
            queries,
            onProgressUpdate=onUpdateProgress,
        )
        return self.parse(raw_response, on_get_total_records=on_get_total_records)
