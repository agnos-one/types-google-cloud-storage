from collections.abc import Mapping

from google.api_core.client_info import ClientInfo
from google.api_core.client_options import ClientOptions
from google.api_core.retry import Retry
from google.auth.credentials import Credentials
from google.cloud.storage.bucket import BlobIterator, Bucket
from google.cloud.storage.retry import ConditionalRetryPolicy

type _Timeout = float | tuple[float, float]
type _Retry = Retry | ConditionalRetryPolicy | None

class Client:
    project: str | None
    def __init__(
        self,
        project: str | None = ...,
        credentials: Credentials | None = None,
        _http: object | None = None,  # a `requests.Session`, such as google-auth's `AuthorizedSession`
        client_info: ClientInfo | None = None,
        client_options: ClientOptions | Mapping[str, object] | None = None,
        use_auth_w_custom_endpoint: bool = True,
        extra_headers: Mapping[str, str] = ...,
        *,
        api_key: str | None = None,
    ) -> None: ...
    def bucket(self, bucket_name: str, user_project: str | None = None, generation: int | None = None) -> Bucket: ...
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
