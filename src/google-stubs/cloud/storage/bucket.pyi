from collections.abc import Iterable, Iterator
from typing import TypedDict, Unpack

from google.api_core.retry import Retry
from google.cloud.storage.blob import Blob
from google.cloud.storage.client import Client
from google.cloud.storage.retry import ConditionalRetryPolicy

type _Timeout = float | tuple[float, float]
type _Retry = Retry | ConditionalRetryPolicy | None
type _ETag = str | Iterable[str] | None

# Stub-only, so import it only for annotations (under `if TYPE_CHECKING:`): at runtime `list_blobs` returns a
# `google.api_core.page_iterator.HTTPIterator` of `Blob`s.
class BlobIterator(Iterable[Blob]):
    next_page_token: str | None
    num_results: int
    # filled in page by page, so it is complete only once the iterator is exhausted
    prefixes: set[str]
    # a generator of the pages; raises `ValueError` once iteration (over pages or blobs) has started
    @property
    def pages(self) -> Iterator[BlobPage]: ...
    # a new generator over all the pages, not the iterator itself; raises `ValueError` once iteration has started
    def __iter__(self) -> Iterator[Blob]: ...
    def __next__(self) -> Blob: ...

# Stub-only, like `BlobIterator`: at runtime a `google.api_core.page_iterator.Page` of `Blob`s.
class BlobPage(Iterator[Blob]):
    @property
    def num_items(self) -> int: ...
    @property
    def remaining(self) -> int: ...
    def __iter__(self) -> BlobPage: ...
    def __next__(self) -> Blob: ...

# the `Blob` constructor arguments `get_blob` passes on through `**kwargs`
class _BlobKwargs(TypedDict, total=False):
    chunk_size: int | None
    kms_key_name: str | None

class Bucket:
    name: str
    def __init__(
        self,
        client: Client | None,
        name: str | None = None,
        user_project: str | None = None,
        generation: int | None = None,
    ) -> None: ...
    @property
    def client(self) -> Client | None: ...
    @property
    def user_project(self) -> str | None: ...
    @property
    def path(self) -> str: ...
    def blob(
        self,
        blob_name: str,
        chunk_size: int | None = None,
        encryption_key: bytes | None = None,
        kms_key_name: str | None = None,
        generation: int | None = None,
    ) -> Blob: ...
    def exists(
        self,
        client: Client | None = None,
        timeout: _Timeout = 60,
        if_etag_match: _ETag = None,
        if_etag_not_match: _ETag = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        retry: _Retry = ...,
    ) -> bool: ...
    def get_blob(
        self,
        blob_name: str,
        client: Client | None = None,
        encryption_key: bytes | None = None,
        generation: int | None = None,
        if_etag_match: _ETag = None,
        if_etag_not_match: _ETag = None,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
        soft_deleted: bool | None = None,
        **kwargs: Unpack[_BlobKwargs],
    ) -> Blob | None: ...
    def list_blobs(
        self,
        max_results: int | None = None,
        page_token: str | None = None,
        prefix: str | None = None,
        delimiter: str | None = None,
        start_offset: str | None = None,
        end_offset: str | None = None,
        include_trailing_delimiter: bool | None = None,
        versions: bool | None = None,
        projection: str = "noAcl",
        fields: str | None = None,
        client: Client | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
        match_glob: str | None = None,
        include_folders_as_prefixes: bool | None = None,
        soft_deleted: bool | None = None,
        page_size: int | None = None,
        filter_: str | None = None,
    ) -> BlobIterator: ...
    def delete_blob(
        self,
        blob_name: str,
        client: Client | None = None,
        generation: int | None = None,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
    ) -> None: ...
