from types import TracebackType
from typing import Self

from google.cloud.storage.client import Client

# At runtime a subclass of `google.cloud.storage._http.Connection`, which is untyped and not stubbed here. Use it as
# a context manager: the calls made through the client inside the `with` block are deferred, and sent as one request
# on exit (unless the block raised).
class Batch:
    def __init__(self, client: Client, raise_exception: bool = True) -> None: ...
    # the `requests.Response` of each deferred request, in order
    def finish(self, raise_exception: bool = True) -> list[object]: ...
    def current(self) -> Batch | None: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None: ...
