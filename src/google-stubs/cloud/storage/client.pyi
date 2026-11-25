from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from datetime import datetime, timedelta
from os import PathLike
from types import TracebackType
from typing import IO, ClassVar, Literal, Never, Self, TypedDict, Unpack

from google.api_core.client_info import ClientInfo
from google.api_core.client_options import ClientOptions
from google.api_core.retry import Retry
from google.auth.credentials import Credentials
from google.cloud.storage.batch import Batch
from google.cloud.storage.blob import Blob
from google.cloud.storage.bucket import BlobIterator, Bucket
from google.cloud.storage.retry import ConditionalRetryPolicy

type _Timeout = float | tuple[float, float]
type _Retry = Retry | ConditionalRetryPolicy | None
type _ETag = str | Iterable[str] | None
type _Checksum = Literal["md5", "crc32c", "auto"] | None
# Stub-only, like `BucketIterator`: one POST policy condition, such as `{"acl": "public-read"}`,
# `["starts-with", "$key", "uploads/"]` or `["content-length-range", 0, 1048576]`. Annotate a list of conditions
# built in a variable as `list[PostPolicyCondition]`.
type PostPolicyCondition = Mapping[str, str] | Sequence[str | int]

# Stub-only, like `BucketIterator`: `client_options` given as a dict, with the options `ClientOptions` takes. It
# has to be a real `dict` (any other mapping raises `AttributeError`), and `api_key=` is written into it. Annotate
# one built in a variable as `ClientOptionsDict`.
class ClientOptionsDict(TypedDict, total=False):
    api_endpoint: str | None
    client_cert_source: Callable[[], tuple[bytes, bytes]] | None
    client_encrypted_cert_source: Callable[[], tuple[str, str, bytes]] | None
    quota_project_id: str | None
    credentials_file: str | None  # deprecated in google-api-core
    scopes: Sequence[str] | None
    api_key: str | None
    api_audience: str | None
    universe_domain: str | None

# the `Client` constructor arguments the `from_service_account_*` factories pass on through `**kwargs`; not
# `credentials`, which the factories set (passing it raises `TypeError`)
class _ClientKwargs(TypedDict, total=False):
    project: str | None
    _http: object | None  # a `requests.Session`, such as google-auth's `AuthorizedSession`
    client_info: ClientInfo | None
    client_options: ClientOptions | ClientOptionsDict | None
    use_auth_w_custom_endpoint: bool
    extra_headers: Mapping[str, str]
    api_key: str | None

# Stub-only, so import it only for annotations (under `if TYPE_CHECKING:`): at runtime `list_buckets` returns a
# `google.api_core.page_iterator.HTTPIterator` of `Bucket`s.
class BucketIterator(Iterable[Bucket]):
    client: Client
    max_results: int | None
    page_number: int
    next_page_token: str | None
    num_results: int
    # a generator of the pages; raises `ValueError` once iteration (over pages or buckets) has started
    @property
    def pages(self) -> Iterator[BucketPage]: ...
    # a new generator over all the pages, not the iterator itself; raises `ValueError` once iteration has started
    def __iter__(self) -> Iterator[Bucket]: ...
    def __next__(self) -> Bucket: ...

# Stub-only, like `BucketIterator`: at runtime a `google.api_core.page_iterator.Page` of `Bucket`s.
class BucketPage(Iterator[Bucket]):
    # the names of the buckets the response couldn't reach (`return_partial_success=True`), set on every page
    unreachable: list[str]
    # the JSON response the page was built from
    @property
    def raw_page(self) -> dict[str, object]: ...
    @property
    def num_items(self) -> int: ...
    @property
    def remaining(self) -> int: ...
    def __iter__(self) -> BucketPage: ...
    def __next__(self) -> Bucket: ...

# what `generate_signed_post_policy_v4` returns
class _SignedPostPolicyV4(TypedDict):
    url: str
    # the form fields to send with the upload: the policy's `fields` plus `key`, `policy`, `x-goog-*`
    fields: dict[str, str]

class Client:
    SCOPE: ClassVar[tuple[str, ...]]
    project: str | None
    def __init__(
        self,
        project: str | None = ...,
        credentials: Credentials | None = None,
        _http: object | None = None,  # a `requests.Session`, such as google-auth's `AuthorizedSession`
        client_info: ClientInfo | None = None,
        client_options: ClientOptions | ClientOptionsDict | None = None,
        use_auth_w_custom_endpoint: bool = True,
        extra_headers: Mapping[str, str] = ...,
        *,
        api_key: str | None = None,
    ) -> None: ...
    # Inherited from `google.cloud.client`. `*args` are passed to the constructor after `project=` from the
    # credentials, so any positional argument raises `TypeError`.
    @classmethod
    def from_service_account_info(
        cls, info: Mapping[str, str], *args: Never, **kwargs: Unpack[_ClientKwargs]
    ) -> Self: ...
    @classmethod
    def from_service_account_json(
        cls, json_credentials_path: str | PathLike[str], *args: Never, **kwargs: Unpack[_ClientKwargs]
    ) -> Self: ...
    @classmethod
    def create_anonymous_client(cls) -> Self: ...
    def close(self) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None: ...
    @property
    def universe_domain(self) -> str: ...
    @property
    def api_endpoint(self) -> str: ...
    def update_user_agent(self, user_agent: str) -> None: ...
    @property
    def current_batch(self) -> Batch | None: ...
    def get_service_account_email(
        self, project: str | None = None, timeout: _Timeout = 60, retry: _Retry = ...
    ) -> str: ...
    def bucket(self, bucket_name: str, user_project: str | None = None, generation: int | None = None) -> Bucket: ...
    def batch(self, raise_exception: bool = True) -> Batch: ...
    def get_bucket(
        self,
        bucket_or_name: Bucket | str,
        timeout: _Timeout = 60,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        retry: _Retry = ...,
        *,
        generation: int | None = None,
        soft_deleted: bool | None = None,
    ) -> Bucket: ...
    def lookup_bucket(
        self,
        bucket_name: str,
        timeout: _Timeout = 60,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        retry: _Retry = ...,
    ) -> Bucket | None: ...
    def create_bucket(
        self,
        bucket_or_name: Bucket | str,
        requester_pays: bool | None = None,  # deprecated: set `Bucket.requester_pays` instead
        project: str | None = None,
        user_project: str | None = None,
        location: str | None = None,
        data_locations: list[str] | None = None,
        predefined_acl: str | None = None,
        predefined_default_object_acl: str | None = None,
        enable_object_retention: bool = False,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
    ) -> Bucket: ...
    def download_blob_to_file(
        self,
        blob_or_uri: Blob | str,
        file_obj: IO[bytes],
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
    def list_blobs(
        self,
        bucket_or_name: Bucket | str,
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
        page_size: int | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
        match_glob: str | None = None,
        include_folders_as_prefixes: bool | None = None,
        soft_deleted: bool | None = None,
        filter_: str | None = None,
    ) -> BlobIterator: ...
    def list_buckets(
        self,
        max_results: int | None = None,
        page_token: str | None = None,
        prefix: str | None = None,
        projection: str = "noAcl",
        fields: str | None = None,
        project: str | None = None,
        page_size: int | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
        *,
        soft_deleted: bool | None = None,
        return_partial_success: bool | None = None,
    ) -> BucketIterator: ...
    def restore_bucket(
        self,
        bucket_name: str,
        generation: int,
        projection: str = "noAcl",
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
    ) -> Bucket: ...
    def generate_signed_post_policy_v4(
        self,
        bucket_name: str,
        blob_name: str,
        expiration: int | datetime | timedelta | None,  # `None`: an hour from now
        conditions: list[PostPolicyCondition] | None = None,  # a list: the policy's own conditions are appended to it
        fields: Mapping[str, str] | None = None,
        credentials: Credentials | None = None,
        virtual_hosted_style: bool = False,
        bucket_bound_hostname: str | None = None,
        scheme: str = "http",
        service_account_email: str | None = None,
        access_token: str | None = None,
    ) -> _SignedPostPolicyV4: ...
