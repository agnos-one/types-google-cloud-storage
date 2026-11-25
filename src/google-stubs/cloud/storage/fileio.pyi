import io
from collections.abc import Buffer
from typing import Literal, TypedDict, Unpack

from google.api_core.retry import Retry
from google.cloud.storage.blob import Blob
from google.cloud.storage.retry import ConditionalRetryPolicy

type _Timeout = float | tuple[float, float]
type _Retry = Retry | ConditionalRetryPolicy | None
type _Checksum = Literal["md5", "crc32c", "auto"] | None

# the `download_as_bytes` arguments `BlobReader` passes on through `**download_kwargs` (`VALID_DOWNLOAD_KWARGS`,
# less `retry`, which is a parameter of its own)
class _DownloadKwargs(TypedDict, total=False):
    if_generation_match: int | None
    if_generation_not_match: int | None
    if_metageneration_match: int | None
    if_metageneration_not_match: int | None
    timeout: _Timeout
    raw_download: bool
    single_shot_download: bool

# the resumable upload arguments `BlobWriter` passes on through `**upload_kwargs` (`VALID_UPLOAD_KWARGS`, less
# `retry`, which is a parameter of its own)
class _UploadKwargs(TypedDict, total=False):
    content_type: str | None
    predefined_acl: str | None
    if_generation_match: int | None
    if_generation_not_match: int | None
    if_metageneration_match: int | None
    if_metageneration_not_match: int | None
    timeout: _Timeout
    checksum: _Checksum

class BlobReader(io.BufferedIOBase):
    def __init__(
        self,
        blob: Blob,
        chunk_size: int | None = None,
        retry: _Retry = ...,
        **download_kwargs: Unpack[_DownloadKwargs],
    ) -> None: ...
    # `size=None` raises `TypeError` at runtime, unlike `BufferedIOBase.read`
    def read(self, size: int = -1) -> bytes: ...  # type: ignore[override]
    def read1(self, size: int = -1) -> bytes: ...
    def seek(self, pos: int, whence: int = 0) -> int: ...
    def close(self) -> None: ...
    @property
    def closed(self) -> bool: ...
    def readable(self) -> bool: ...
    def writable(self) -> bool: ...
    def seekable(self) -> bool: ...

class BlobWriter(io.BufferedIOBase):
    def __init__(
        self,
        blob: Blob,
        chunk_size: int | None = None,
        ignore_flush: bool = False,
        retry: _Retry = ...,
        **upload_kwargs: Unpack[_UploadKwargs],
    ) -> None: ...
    def write(self, b: Buffer) -> int: ...
    def tell(self) -> int: ...
    # raises `io.UnsupportedOperation` unless `ignore_flush` is set; `close()` finishes the upload
    def flush(self) -> None: ...
    def close(self) -> None: ...
    # cancels the resumable upload
    def terminate(self) -> None: ...
    @property
    def closed(self) -> bool: ...
    def readable(self) -> bool: ...
    def writable(self) -> bool: ...
    def seekable(self) -> bool: ...
