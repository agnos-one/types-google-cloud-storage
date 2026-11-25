from collections.abc import Iterable, Mapping
from datetime import datetime, timedelta
from os import PathLike
from typing import IO, Literal

from google.api_core.retry import Retry
from google.auth.credentials import Credentials
from google.cloud.storage.bucket import Bucket
from google.cloud.storage.client import Client
from google.cloud.storage.retry import ConditionalRetryPolicy

type _Timeout = float | tuple[float, float]
type _Retry = Retry | ConditionalRetryPolicy | None
type _ETag = str | Iterable[str] | None
type _Checksum = Literal["md5", "crc32c", "auto"] | None
type _Path = str | PathLike[str]

class Blob:
    name: str
    # Metadata: `None` until the blob is loaded (`reload`, `get_blob`, `list_blobs`) or the field is set locally.
    cache_control: str | None
    content_disposition: str | None
    content_encoding: str | None
    content_language: str | None
    content_type: str | None
    crc32c: str | None
    md5_hash: str | None
    storage_class: str | None
    @property
    def metadata(self) -> dict[str, str] | None: ...
    # a `None` value deletes that key on the next `patch()`
    @metadata.setter
    def metadata(self, value: Mapping[str, str | None] | None) -> None: ...
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
    @property
    def path(self) -> str: ...
    @property
    def public_url(self) -> str: ...
    @property
    def size(self) -> int | None: ...
    @property
    def etag(self) -> str | None: ...
    @property
    def generation(self) -> int | None: ...
    @property
    def time_created(self) -> datetime | None: ...
    @property
    def updated(self) -> datetime | None: ...
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
