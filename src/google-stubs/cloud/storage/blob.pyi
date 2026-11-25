from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime, timedelta
from io import TextIOWrapper
from os import PathLike
from typing import IO, ClassVar, Literal, Self, TypedDict, Unpack, overload
from warnings import deprecated

from google.api_core.iam import Policy
from google.api_core.retry import Retry
from google.auth.credentials import Credentials
from google.cloud.storage.bucket import Bucket
from google.cloud.storage.client import Client
from google.cloud.storage.fileio import BlobReader, BlobWriter
from google.cloud.storage.retry import ConditionalRetryPolicy

type _Timeout = float | tuple[float, float]
type _Retry = Retry | ConditionalRetryPolicy | None
type _ETag = str | Iterable[str] | None
type _Checksum = Literal["md5", "crc32c", "auto"] | None
type _Path = str | PathLike[str]

# the `BlobReader` arguments `open` passes on through `**kwargs` in the read modes
class _OpenReadKwargs(TypedDict, total=False):
    if_generation_match: int | None
    if_generation_not_match: int | None
    if_metageneration_match: int | None
    if_metageneration_not_match: int | None
    timeout: _Timeout
    retry: _Retry
    raw_download: bool
    single_shot_download: bool

# the `BlobWriter` arguments `open` passes on through `**kwargs` in the write modes
class _OpenWriteKwargs(TypedDict, total=False):
    content_type: str | None
    predefined_acl: str | None
    if_generation_match: int | None
    if_generation_not_match: int | None
    if_metageneration_match: int | None
    if_metageneration_not_match: int | None
    timeout: _Timeout
    checksum: _Checksum
    retry: _Retry

class Blob:
    STORAGE_CLASSES: ClassVar[tuple[str, ...]]
    name: str
    # must be a multiple of 256 KiB (the setter raises `ValueError` otherwise)
    chunk_size: int | None
    # customer-supplied encryption key (32 bytes)
    encryption_key: bytes | None
    kms_key_name: str | None
    # Metadata: `None` until the blob is loaded (`reload`, `get_blob`, `list_blobs`) or the field is set locally.
    cache_control: str | None
    content_disposition: str | None
    content_encoding: str | None
    content_language: str | None
    content_type: str | None
    crc32c: str | None
    md5_hash: str | None
    storage_class: str | None
    event_based_hold: bool | None
    temporary_hold: bool | None
    custom_time: datetime | None
    @property
    def metadata(self) -> dict[str, str] | None: ...
    # a `None` value deletes that key on the next `patch()`
    @metadata.setter
    def metadata(self, value: Mapping[str, str | None] | None) -> None: ...
    # never `None`: an empty `ObjectContexts` until the blob is loaded or the contexts are set
    @property
    def contexts(self) -> ObjectContexts: ...
    # a dict in the JSON API shape, `{"custom": {key: {"value": ...}}}`, is accepted too; it is sent as JSON as is
    @contexts.setter
    def contexts(self, value: ObjectContexts | Mapping[str, Mapping[str, Mapping[str, str | None]]] | None) -> None: ...
    def __init__(
        self,
        name: str,
        bucket: Bucket,
        chunk_size: int | None = None,
        encryption_key: bytes | None = None,
        kms_key_name: str | None = None,
        generation: int | None = None,
    ) -> None: ...
    @property
    def bucket(self) -> Bucket: ...
    @staticmethod
    def path_helper(bucket_path: str, blob_name: str) -> str: ...
    @property
    def path(self) -> str: ...
    @property
    def client(self) -> Client | None: ...
    @property
    def user_project(self) -> str | None: ...
    @property
    def public_url(self) -> str: ...
    @property
    def size(self) -> int | None: ...
    @property
    def etag(self) -> str | None: ...
    @property
    def generation(self) -> int | None: ...
    @property
    def metageneration(self) -> int | None: ...
    @property
    def id(self) -> str | None: ...
    @property
    def media_link(self) -> str | None: ...
    @property
    def self_link(self) -> str | None: ...
    # set only on objects created by `compose`
    @property
    def component_count(self) -> int | None: ...
    # `{"entity": ..., "entityId": ...}`
    @property
    def owner(self) -> dict[str, str] | None: ...
    @property
    def time_created(self) -> datetime | None: ...
    @property
    def updated(self) -> datetime | None: ...
    @property
    def time_deleted(self) -> datetime | None: ...
    @property
    def retention_expiration_time(self) -> datetime | None: ...
    # never `None`: the setters of the returned `Retention` mark the blob's retention for the next `patch()`
    @property
    def retention(self) -> Retention: ...
    # set only on soft-deleted objects
    @property
    def soft_delete_time(self) -> datetime | None: ...
    @property
    def hard_delete_time(self) -> datetime | None: ...
    @property
    def finalized_time(self) -> datetime | None: ...
    @classmethod
    def from_uri(cls, uri: str, client: Client | None = None) -> Self: ...
    # returns `Blob.from_uri(...)`, so a `Blob` rather than `Self`
    @classmethod
    @deprecated("Blob.from_string() is deprecated; use Blob.from_uri() instead.")
    def from_string(cls, uri: str, client: Client | None = None) -> Blob: ...
    def exists(
        self,
        client: Client | None = None,
        if_etag_match: _ETag = None,
        if_etag_not_match: _ETag = None,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
        soft_deleted: bool | None = None,
    ) -> bool: ...
    def reload(
        self,
        client: Client | None = None,
        projection: str = "noAcl",
        if_etag_match: _ETag = None,
        if_etag_not_match: _ETag = None,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
        soft_deleted: bool | None = None,
    ) -> None: ...
    def patch(
        self,
        client: Client | None = None,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
        override_unlocked_retention: bool = False,
    ) -> None: ...
    def update(
        self,
        client: Client | None = None,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
        override_unlocked_retention: bool = False,
    ) -> None: ...
    def delete(
        self,
        client: Client | None = None,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
    ) -> None: ...
    def download_to_file(
        self,
        file_obj: IO[bytes],
        client: Client | None = None,
        start: int | None = None,
        end: int | None = None,
        raw_download: bool = False,
        if_etag_match: _ETag = None,
        if_etag_not_match: _ETag = None,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        timeout: _Timeout = 60,
        checksum: _Checksum = "auto",
        retry: _Retry = ...,
        single_shot_download: bool = False,
    ) -> None: ...
    def download_as_bytes(
        self,
        client: Client | None = None,
        start: int | None = None,
        end: int | None = None,
        raw_download: bool = False,
        if_etag_match: _ETag = None,
        if_etag_not_match: _ETag = None,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        timeout: _Timeout = 60,
        checksum: _Checksum = "auto",
        retry: _Retry = ...,
        single_shot_download: bool = False,
    ) -> bytes: ...
    def download_as_text(
        self,
        client: Client | None = None,
        start: int | None = None,
        end: int | None = None,
        raw_download: bool = False,
        encoding: str | None = None,
        if_etag_match: _ETag = None,
        if_etag_not_match: _ETag = None,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
        single_shot_download: bool = False,
    ) -> str: ...
    def download_to_filename(
        self,
        filename: _Path,
        client: Client | None = None,
        start: int | None = None,
        end: int | None = None,
        raw_download: bool = False,
        if_etag_match: _ETag = None,
        if_etag_not_match: _ETag = None,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        timeout: _Timeout = 60,
        checksum: _Checksum = "auto",
        retry: _Retry = ...,
        single_shot_download: bool = False,
    ) -> None: ...
    def upload_from_string(
        self,
        data: bytes | str,
        content_type: str = "text/plain",
        client: Client | None = None,
        predefined_acl: str | None = None,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        timeout: _Timeout = 60,
        checksum: _Checksum = "auto",
        retry: _Retry = ...,
        crc32c_checksum_value: str | None = None,
    ) -> None: ...
    def upload_from_file(
        self,
        file_obj: IO[bytes],
        rewind: bool = False,
        size: int | None = None,
        content_type: str | None = None,
        client: Client | None = None,
        predefined_acl: str | None = None,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        timeout: _Timeout = 60,
        checksum: _Checksum = "auto",
        retry: _Retry = ...,
        crc32c_checksum_value: str | None = None,
    ) -> None: ...
    def upload_from_filename(
        self,
        filename: _Path,
        content_type: str | None = None,
        client: Client | None = None,
        predefined_acl: str | None = None,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        timeout: _Timeout = 60,
        checksum: _Checksum = "auto",
        retry: _Retry = ...,
        crc32c_checksum_value: str | None = None,
    ) -> None: ...
    def generate_signed_url(
        self,
        expiration: int | datetime | timedelta | None = None,
        api_access_endpoint: str | None = None,
        method: str = "GET",
        content_md5: str | None = None,
        content_type: str | None = None,
        response_disposition: str | None = None,
        response_type: str | None = None,
        generation: int | None = None,
        headers: Mapping[str, str] | None = None,
        query_parameters: Mapping[str, str] | None = None,
        client: Client | None = None,
        credentials: Credentials | None = None,
        version: Literal["v2", "v4"] | None = None,
        service_account_email: str | None = None,
        access_token: str | None = None,
        virtual_hosted_style: bool = False,
        bucket_bound_hostname: str | None = None,
        scheme: str = "http",
    ) -> str: ...
    # returns the session URL; the upload itself is a PUT to it
    def create_resumable_upload_session(
        self,
        content_type: str | None = None,
        size: int | None = None,
        origin: str | None = None,
        client: Client | None = None,
        timeout: _Timeout = 60,
        checksum: _Checksum = "auto",
        predefined_acl: str | None = None,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        retry: _Retry = ...,
    ) -> str: ...
    def get_iam_policy(
        self,
        client: Client | None = None,
        requested_policy_version: int | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
    ) -> Policy: ...
    def set_iam_policy(
        self,
        policy: Policy,
        client: Client | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
    ) -> Policy: ...
    def test_iam_permissions(
        self,
        permissions: Sequence[str],
        client: Client | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
    ) -> list[str]: ...
    def make_public(
        self,
        client: Client | None = None,
        timeout: _Timeout = 60,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        retry: _Retry = ...,
    ) -> None: ...
    def make_private(
        self,
        client: Client | None = None,
        timeout: _Timeout = 60,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        retry: _Retry = ...,
    ) -> None: ...
    # The deprecated list forms of `if_generation_match` and `if_metageneration_match` are left out.
    # `if_source_generation_match` matches `sources` item by item; a `None` item sets no precondition.
    def compose(
        self,
        sources: Sequence[Blob],
        client: Client | None = None,
        timeout: _Timeout = 60,
        if_generation_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_source_generation_match: Sequence[int | None] | None = None,
        retry: _Retry = ...,
        destination_contexts: ObjectContexts | None = None,
        delete_source_objects: bool | None = None,
    ) -> None: ...
    # returns `(token, bytes_rewritten, total_bytes)`; `token` is `None` once the rewrite is complete
    def rewrite(
        self,
        source: Blob,
        token: str | None = None,
        client: Client | None = None,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        if_source_generation_match: int | None = None,
        if_source_generation_not_match: int | None = None,
        if_source_metageneration_match: int | None = None,
        if_source_metageneration_not_match: int | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
        destination_contexts: ObjectContexts | None = None,
    ) -> tuple[str | None, int, int]: ...
    def update_storage_class(
        self,
        new_class: str,
        client: Client | None = None,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        if_source_generation_match: int | None = None,
        if_source_generation_not_match: int | None = None,
        if_source_metageneration_match: int | None = None,
        if_source_metageneration_not_match: int | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
    ) -> None: ...
    # Only these six modes are accepted (others raise `NotImplementedError`), so there is no overload for a plain
    # `str`. The parameters that raise `ValueError` in a mode are narrowed to the values it accepts: `encoding`,
    # `errors` and `newline` are for text modes only, and `ignore_flush` can't be set when reading or be `False`
    # when writing text.
    @overload
    def open(
        self,
        mode: Literal["r", "rt"] = "r",
        chunk_size: int | None = None,
        ignore_flush: Literal[False] | None = None,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
        **kwargs: Unpack[_OpenReadKwargs],
    ) -> TextIOWrapper: ...
    @overload
    def open(
        self,
        mode: Literal["w", "wt"],
        chunk_size: int | None = None,
        ignore_flush: Literal[True] | None = None,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
        **kwargs: Unpack[_OpenWriteKwargs],
    ) -> TextIOWrapper: ...
    @overload
    def open(
        self,
        mode: Literal["rb"],
        chunk_size: int | None = None,
        ignore_flush: Literal[False] | None = None,
        encoding: None = None,
        errors: None = None,
        newline: None = None,
        **kwargs: Unpack[_OpenReadKwargs],
    ) -> BlobReader: ...
    @overload
    def open(
        self,
        mode: Literal["wb"],
        chunk_size: int | None = None,
        ignore_flush: bool | None = None,
        encoding: None = None,
        errors: None = None,
        newline: None = None,
        **kwargs: Unpack[_OpenWriteKwargs],
    ) -> BlobWriter: ...

# A dict in the JSON API shape (`mode`, `retainUntilTime`, `retentionExpirationTime`); the setters update it and
# mark the blob's retention for the next `patch()`.
class Retention(dict[str, str | None]):
    def __init__(
        self,
        blob: Blob,
        mode: str | None = None,
        retain_until_time: datetime | None = None,
        retention_expiration_time: datetime | None = None,
    ) -> None: ...
    @classmethod
    def from_api_repr(cls, resource: Mapping[str, str | None], blob: Blob) -> Self: ...
    @property
    def blob(self) -> Blob: ...
    # "Unlocked" or "Locked"
    @property
    def mode(self) -> str | None: ...
    @mode.setter
    def mode(self, value: str | None) -> None: ...
    @property
    def retain_until_time(self) -> datetime | None: ...
    @retain_until_time.setter
    def retain_until_time(self, value: datetime | None) -> None: ...
    @property
    def retention_expiration_time(self) -> datetime | None: ...

# A dict in the JSON API shape (`value`, `createTime`, `updateTime`).
class ObjectCustomContextPayload(dict[str, str | None]):
    def __init__(self, value: str | None = None) -> None: ...
    @property
    def value(self) -> str | None: ...
    # marks the blob's contexts for the next `patch()`, once the payload belongs to a blob's `ObjectContexts`
    @value.setter
    def value(self, value: str | None) -> None: ...
    @property
    def create_time(self) -> datetime | None: ...
    @property
    def update_time(self) -> datetime | None: ...

# A dict in the JSON API shape, `{"custom": {key: payload}}`.
class ObjectContexts(dict[str, dict[str, ObjectCustomContextPayload]]):
    # `custom` must be a `dict` of `ObjectCustomContextPayload`s (`ValueError` otherwise)
    def __init__(self, blob: Blob, custom: dict[str, ObjectCustomContextPayload] | None = None) -> None: ...
    @classmethod
    def from_api_repr(cls, resource: Mapping[str, Mapping[str, Mapping[str, str | None]]], blob: Blob) -> Self: ...
    @property
    def blob(self) -> Blob: ...
    @property
    def custom(self) -> dict[str, ObjectCustomContextPayload]: ...
    # marks the blob's contexts for the next `patch()`; `None` clears them
    @custom.setter
    def custom(self, value: dict[str, ObjectCustomContextPayload] | None) -> None: ...
