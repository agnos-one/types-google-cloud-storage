from collections.abc import Iterable, Mapping, Sequence
from os import PathLike
from typing import IO, Final, Literal, TypedDict

from google.api_core.retry import Retry
from google.cloud.storage.blob import Blob
from google.cloud.storage.bucket import Bucket
from google.cloud.storage.client import Client
from google.cloud.storage.retry import ConditionalRetryPolicy

type _Timeout = float | tuple[float, float]
type _Retry = Retry | ConditionalRetryPolicy | None
type _ETag = str | Iterable[str] | None
type _Checksum = Literal["md5", "crc32c", "auto"] | None
type _Path = str | PathLike[str]
type _WorkerType = Literal["process", "thread"]
# a file name or, with `worker_type=THREAD` only, a file object
type _FileOrName = str | IO[bytes]

TM_DEFAULT_CHUNK_SIZE: int
DEFAULT_MAX_WORKERS: int
MAX_CRC32C_ZERO_ARRAY_SIZE: int
METADATA_HEADER_TRANSLATION: dict[str, str]
PROCESS: Final = "process"
THREAD: Final = "thread"
DOWNLOAD_CRC32C_MISMATCH_TEMPLATE: str

# The TypedDicts below are stub-only, so import them only for annotations (under `if TYPE_CHECKING:`): at runtime
# these arguments are plain `dict`s.

# `upload_kwargs`: the keyword arguments of `Blob.upload_from_filename`, which the uploads take whether they read a
# file name or a file object
class UploadKwargs(TypedDict, total=False):
    content_type: str | None
    client: Client | None
    predefined_acl: str | None
    if_generation_match: int | None  # set to 0 by `skip_if_exists=True`
    if_generation_not_match: int | None
    if_metageneration_match: int | None
    if_metageneration_not_match: int | None
    timeout: _Timeout
    checksum: _Checksum
    retry: _Retry
    crc32c_checksum_value: str | None

# `download_kwargs` of `download_many` and `download_many_to_path`: the keyword arguments of
# `Blob.download_to_filename`
class DownloadKwargs(TypedDict, total=False):
    client: Client | None
    start: int | None
    end: int | None
    raw_download: bool
    if_etag_match: _ETag
    if_etag_not_match: _ETag
    if_generation_match: int | None
    if_generation_not_match: int | None
    if_metageneration_match: int | None
    if_metageneration_not_match: int | None
    timeout: _Timeout
    checksum: _Checksum
    retry: _Retry
    single_shot_download: bool

# `download_kwargs` of `download_chunks_concurrently`: `DownloadKwargs` without `start`, `end` and `checksum`, which
# raise `ValueError` (use `crc32c_checksum` instead of `checksum`)
class ChunkDownloadKwargs(TypedDict, total=False):
    client: Client | None
    raw_download: bool
    if_etag_match: _ETag
    if_etag_not_match: _ETag
    if_generation_match: int | None
    if_generation_not_match: int | None
    if_metageneration_match: int | None
    if_metageneration_not_match: int | None
    timeout: _Timeout
    retry: _Retry
    single_shot_download: bool

# `blob_constructor_kwargs`: the `Bucket.blob` arguments other than the blob name
class BlobConstructorKwargs(TypedDict, total=False):
    chunk_size: int | None
    encryption_key: bytes | None
    kms_key_name: str | None
    generation: int | None

# The `*_many*` functions return a result per item, in order: `None` for a success, or the exception it raised
# (with `raise_exception=False`, and for the 412s `skip_if_exists=True` causes on uploads). Items skipped because the
# file exists are left out by `download_many` (so its results no longer line up with the inputs), and get a
# `UserWarning` from `download_many_to_path`, which also gives one to each blob whose path is invalid.

def upload_many(
    file_blob_pairs: Iterable[tuple[_FileOrName, Blob]],
    skip_if_exists: bool = False,
    upload_kwargs: UploadKwargs | None = None,
    threads: int | None = None,  # deprecated: use `worker_type=THREAD` and `max_workers`
    deadline: float | None = None,
    raise_exception: bool = False,
    worker_type: _WorkerType = "process",
    max_workers: int = 8,
) -> list[None | Exception]: ...
def download_many(
    blob_file_pairs: Iterable[tuple[Blob, _FileOrName]],
    download_kwargs: DownloadKwargs | None = None,
    threads: int | None = None,  # deprecated: use `worker_type=THREAD` and `max_workers`
    deadline: float | None = None,
    raise_exception: bool = False,
    worker_type: _WorkerType = "process",
    max_workers: int = 8,
    *,
    skip_if_exists: bool = False,
) -> list[None | Exception]: ...
def upload_many_from_filenames(
    bucket: Bucket,
    filenames: Iterable[str],
    source_directory: _Path = "",
    blob_name_prefix: str = "",
    skip_if_exists: bool = False,
    blob_constructor_kwargs: BlobConstructorKwargs | None = None,
    upload_kwargs: UploadKwargs | None = None,
    threads: int | None = None,  # deprecated: use `worker_type=THREAD` and `max_workers`
    deadline: float | None = None,
    raise_exception: bool = False,
    worker_type: _WorkerType = "process",
    max_workers: int = 8,
    *,
    additional_blob_attributes: Mapping[str, object] | None = None,  # set with `setattr` on each blob
) -> list[None | Exception]: ...
def download_many_to_path(
    bucket: Bucket,
    blob_names: Sequence[str],
    destination_directory: _Path = "",
    blob_name_prefix: str = "",
    download_kwargs: DownloadKwargs | None = None,
    threads: int | None = None,  # deprecated: use `worker_type=THREAD` and `max_workers`
    deadline: float | None = None,
    create_directories: bool = True,
    raise_exception: bool = False,
    worker_type: _WorkerType = "process",
    max_workers: int = 8,
    *,
    skip_if_exists: bool = False,
) -> list[None | Exception]: ...
def download_chunks_concurrently(
    blob: Blob,
    filename: _Path,
    chunk_size: int = 33554432,
    download_kwargs: ChunkDownloadKwargs | None = None,
    deadline: float | None = None,
    worker_type: _WorkerType = "process",
    max_workers: int = 8,
    *,
    crc32c_checksum: bool = True,
) -> None: ...
def upload_chunks_concurrently(
    filename: _Path,
    blob: Blob,
    content_type: str | None = None,
    chunk_size: int = 33554432,
    deadline: float | None = None,
    worker_type: _WorkerType = "process",
    max_workers: int = 8,
    *,
    checksum: _Checksum = "auto",
    timeout: _Timeout = 60,
    retry: Retry | None = ...,  # no `ConditionalRetryPolicy`: the XML multipart upload takes no preconditions
) -> None: ...
