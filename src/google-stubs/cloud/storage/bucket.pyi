from collections.abc import Callable, Collection, Iterable, Iterator, Mapping, Sequence
from datetime import date, datetime, timedelta
from typing import ClassVar, Literal, NotRequired, Self, TypedDict, Unpack
from warnings import deprecated

from google.api_core.iam import Policy
from google.api_core.retry import Retry
from google.auth.credentials import Credentials
from google.cloud.storage.blob import Blob, ObjectContexts
from google.cloud.storage.client import Client, PostPolicyCondition
from google.cloud.storage.ip_filter import IPFilter
from google.cloud.storage.retry import ConditionalRetryPolicy

type _Timeout = float | tuple[float, float]
type _Retry = Retry | ConditionalRetryPolicy | None
type _ETag = str | Iterable[str] | None
# the JSON values of a lifecycle rule's `condition` (and `action`) object
type _ConditionValue = int | str | bool | list[str]

# Stub-only, so import it only for annotations (under `if TYPE_CHECKING:`): at runtime `list_blobs` returns a
# `google.api_core.page_iterator.HTTPIterator` of `Blob`s.
class BlobIterator(Iterable[Blob]):
    client: Client
    max_results: int | None
    page_number: int
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
    # the prefixes of this page; `BlobIterator.prefixes` collects those of the pages fetched so far
    prefixes: tuple[str, ...]
    # the JSON response the page was built from
    @property
    def raw_page(self) -> dict[str, object]: ...
    @property
    def num_items(self) -> int: ...
    @property
    def remaining(self) -> int: ...
    def __iter__(self) -> BlobPage: ...
    def __next__(self) -> Blob: ...

# Stub-only, like `BlobIterator`: at runtime a plain `dict`. One entry of `Bucket.cors`, as in the JSON API's
# bucket resource.
class CorsPolicy(TypedDict, total=False):
    origin: list[str]
    method: list[str]
    responseHeader: list[str]
    maxAgeSeconds: int

# what `Bucket.get_logging` returns
class _Logging(TypedDict):
    logBucket: str
    logObjectPrefix: NotRequired[str]

# what `Bucket.generate_upload_policy` returns: the form fields that sign the upload
class _UploadPolicyFields(TypedDict):
    bucket: str
    GoogleAccessId: str
    policy: str
    signature: str

# what `Bucket.owner` returns
class _Owner(TypedDict):
    entity: str
    entityId: NotRequired[str]

# the `Blob` constructor arguments `get_blob` passes on through `**kwargs`
class _BlobKwargs(TypedDict, total=False):
    chunk_size: int | None
    kms_key_name: str | None

# the `LifecycleRuleConditions` arguments the lifecycle rule classes and `Bucket.add_lifecycle_*_rule` take
# through `**kw`; at least one is required, or they raise `ValueError`
class _LifecycleRuleConditionsKwargs(TypedDict, total=False):
    age: int | None
    created_before: date | None
    is_live: bool | None
    matches_storage_class: list[str] | None
    number_of_newer_versions: int | None
    days_since_custom_time: int | None
    custom_time_before: date | None
    days_since_noncurrent_time: int | None
    noncurrent_time_before: date | None
    matches_prefix: list[str] | None
    matches_suffix: list[str] | None

# the conditions Cloud Storage supports for `LifecycleRuleAbortIncompleteMultipartUpload` (the docstring, which
# names `age` only, predates the other two; the runtime passes any condition on, and the API rejects the rest)
class _AbortIncompleteMultipartUploadKwargs(TypedDict, total=False):
    age: int | None
    matches_prefix: list[str] | None
    matches_suffix: list[str] | None

# the keys `SoftDeletePolicy` reads from `**kw`
class _SoftDeletePolicyKwargs(TypedDict, total=False):
    retention_duration_seconds: int | None
    effective_time: datetime | None

class LifecycleRuleConditions(dict[str, _ConditionValue]):
    def __init__(
        self,
        age: int | None = None,
        created_before: date | None = None,
        is_live: bool | None = None,
        matches_storage_class: list[str] | None = None,
        number_of_newer_versions: int | None = None,
        days_since_custom_time: int | None = None,
        custom_time_before: date | None = None,
        days_since_noncurrent_time: int | None = None,
        noncurrent_time_before: date | None = None,
        matches_prefix: list[str] | None = None,
        matches_suffix: list[str] | None = None,
        _factory: bool = False,
    ) -> None: ...
    @classmethod
    def from_api_repr(cls, resource: Mapping[str, object]) -> Self: ...
    @property
    def age(self) -> int | None: ...
    @property
    def created_before(self) -> date | None: ...
    @property
    def is_live(self) -> bool | None: ...
    @property
    def matches_prefix(self) -> list[str] | None: ...
    @property
    def matches_storage_class(self) -> list[str] | None: ...
    @property
    def matches_suffix(self) -> list[str] | None: ...
    @property
    def number_of_newer_versions(self) -> int | None: ...
    @property
    def days_since_custom_time(self) -> int | None: ...
    @property
    def custom_time_before(self) -> date | None: ...
    @property
    def days_since_noncurrent_time(self) -> int | None: ...
    @property
    def noncurrent_time_before(self) -> date | None: ...

# The lifecycle rules are `{"action": {"type": ...}, "condition": {...}}` mappings.
class LifecycleRuleDelete(dict[str, dict[str, _ConditionValue]]):
    def __init__(self, **kw: Unpack[_LifecycleRuleConditionsKwargs]) -> None: ...
    @classmethod
    def from_api_repr(cls, resource: Mapping[str, object]) -> Self: ...

class LifecycleRuleSetStorageClass(dict[str, dict[str, _ConditionValue]]):
    # `storage_class`: one of `Bucket.STORAGE_CLASSES`
    def __init__(self, storage_class: str, **kw: Unpack[_LifecycleRuleConditionsKwargs]) -> None: ...
    @classmethod
    def from_api_repr(cls, resource: Mapping[str, object]) -> Self: ...

class LifecycleRuleAbortIncompleteMultipartUpload(dict[str, dict[str, _ConditionValue]]):
    def __init__(self, **kw: Unpack[_AbortIncompleteMultipartUploadKwargs]) -> None: ...
    @classmethod
    def from_api_repr(cls, resource: Mapping[str, object]) -> Self: ...

# The setters update the bucket's pending changes; `patch()` the bucket to save them.
class IAMConfiguration(dict[str, str | dict[str, bool | str]]):
    # "inherited" (the default) or "enforced"
    public_access_prevention: str
    uniform_bucket_level_access_enabled: bool
    def __init__(
        self,
        bucket: Bucket,
        public_access_prevention: str = ...,
        uniform_bucket_level_access_enabled: bool = ...,
        uniform_bucket_level_access_locked_time: datetime = ...,
        bucket_policy_only_enabled: bool = ...,  # deprecated alias of `uniform_bucket_level_access_enabled`
        bucket_policy_only_locked_time: datetime = ...,  # deprecated alias of `uniform_bucket_level_access_locked_time`
    ) -> None: ...
    @classmethod
    def from_api_repr(cls, resource: Mapping[str, object], bucket: Bucket) -> Self: ...
    @property
    def bucket(self) -> Bucket: ...
    @property
    def uniform_bucket_level_access_locked_time(self) -> datetime | None: ...
    @property
    @deprecated("Use IAMConfiguration.uniform_bucket_level_access_enabled instead.")
    def bucket_policy_only_enabled(self) -> bool: ...
    @bucket_policy_only_enabled.setter
    @deprecated("Use IAMConfiguration.uniform_bucket_level_access_enabled instead.")
    def bucket_policy_only_enabled(self, value: bool) -> None: ...
    @property
    @deprecated("Use IAMConfiguration.uniform_bucket_level_access_locked_time instead.")
    def bucket_policy_only_locked_time(self) -> datetime | None: ...

class EncryptionEnforcementConfig(dict[str, str]):
    def __init__(self, restriction_mode: Literal["FullyRestricted", "NotRestricted"] | None = None) -> None: ...
    @classmethod
    def from_api_repr(cls, resource: Mapping[str, object]) -> Self: ...
    @property
    def restriction_mode(self) -> str | None: ...
    @restriction_mode.setter
    def restriction_mode(self, value: Literal["FullyRestricted", "NotRestricted"]) -> None: ...
    @property
    def effective_time(self) -> datetime | None: ...

# Like `IAMConfiguration`, the setters update the bucket's pending changes.
class BucketEncryption(dict[str, str | dict[str, str] | None]):
    # `None` clears the key
    default_kms_key_name: str | None
    def __init__(
        self,
        bucket: Bucket,
        default_kms_key_name: str | None = None,
        google_managed_encryption_enforcement_config: EncryptionEnforcementConfig | None = None,
        customer_managed_encryption_enforcement_config: EncryptionEnforcementConfig | None = None,
        customer_supplied_encryption_enforcement_config: EncryptionEnforcementConfig | None = None,
    ) -> None: ...
    @classmethod
    def from_api_repr(cls, resource: Mapping[str, object], bucket: Bucket) -> Self: ...
    @property
    def bucket(self) -> Bucket: ...
    @property
    def google_managed_encryption_enforcement_config(self) -> EncryptionEnforcementConfig | None: ...
    @google_managed_encryption_enforcement_config.setter
    def google_managed_encryption_enforcement_config(
        self, value: EncryptionEnforcementConfig | Mapping[str, str]
    ) -> None: ...
    @property
    def customer_managed_encryption_enforcement_config(self) -> EncryptionEnforcementConfig | None: ...
    @customer_managed_encryption_enforcement_config.setter
    def customer_managed_encryption_enforcement_config(
        self, value: EncryptionEnforcementConfig | Mapping[str, str]
    ) -> None: ...
    @property
    def customer_supplied_encryption_enforcement_config(self) -> EncryptionEnforcementConfig | None: ...
    @customer_supplied_encryption_enforcement_config.setter
    def customer_supplied_encryption_enforcement_config(
        self, value: EncryptionEnforcementConfig | Mapping[str, str]
    ) -> None: ...

# Like `IAMConfiguration`, the setter updates the bucket's pending changes.
class SoftDeletePolicy(dict[str, int | str | None]):
    def __init__(self, bucket: Bucket, **kw: Unpack[_SoftDeletePolicyKwargs]) -> None: ...
    @classmethod
    def from_api_repr(cls, resource: Mapping[str, object], bucket: Bucket) -> Self: ...
    @property
    def bucket(self) -> Bucket: ...
    @property
    def retention_duration_seconds(self) -> int | None: ...
    @retention_duration_seconds.setter
    def retention_duration_seconds(self, value: int) -> None: ...
    @property
    def effective_time(self) -> datetime | None: ...

class Bucket:
    STORAGE_CLASSES: ClassVar[tuple[str, ...]]
    name: str
    # Metadata: `None` until the bucket is loaded (`reload`, `get_bucket`, `list_buckets`) or the field is set
    # locally, except the three typed `bool`, which read `False` until then. The setters, here and below, record a
    # change that `patch()` sends.
    default_event_based_hold: bool | None
    default_kms_key_name: str | None
    versioning_enabled: bool
    requester_pays: bool
    autoclass_enabled: bool
    def __init__(
        self,
        client: Client | None,
        name: str | None = None,
        user_project: str | None = None,
        generation: int | None = None,
    ) -> None: ...
    @property
    def client(self) -> Client | None: ...
    # "ASYNC_TURBO" or "DEFAULT"
    @property
    def rpo(self) -> str | None: ...
    @rpo.setter
    def rpo(self, value: str) -> None: ...
    @property
    def user_project(self) -> str | None: ...
    @property
    def generation(self) -> int | None: ...
    # set only for soft-deleted buckets
    @property
    def soft_delete_time(self) -> datetime | None: ...
    @property
    def hard_delete_time(self) -> datetime | None: ...
    @classmethod
    def from_uri(cls, uri: str, client: Client | None = None) -> Self: ...
    @classmethod
    @deprecated("Use Bucket.from_uri() instead.")
    def from_string(cls, uri: str, client: Client | None = None) -> Bucket: ...
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
    def create(
        self,
        client: Client | None = None,
        project: str | None = None,
        location: str | None = None,
        predefined_acl: str | None = None,
        predefined_default_object_acl: str | None = None,
        enable_object_retention: bool = False,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
    ) -> None: ...
    def update(
        self,
        client: Client | None = None,
        timeout: _Timeout = 60,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        retry: _Retry = ...,
    ) -> None: ...
    def reload(
        self,
        client: Client | None = None,
        projection: str = "noAcl",
        timeout: _Timeout = 60,
        if_etag_match: _ETag = None,
        if_etag_not_match: _ETag = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        retry: _Retry = ...,
        soft_deleted: bool | None = None,
    ) -> None: ...
    def patch(
        self,
        client: Client | None = None,
        timeout: _Timeout = 60,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        retry: _Retry = ...,
    ) -> None: ...
    @staticmethod
    def path_helper(bucket_name: str) -> str: ...
    @property
    def path(self) -> str: ...
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
    def delete(
        self,
        force: bool = False,
        client: Client | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
    ) -> None: ...
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
    # `on_error` is called with each item of `blobs` that raises `NotFound`; without it, `NotFound` propagates.
    # The `if_*` lists, if given, hold one precondition per blob, in the same order.
    def delete_blobs[B: Blob | str](
        self,
        blobs: Collection[B],
        on_error: Callable[[B], object] | None = None,
        client: Client | None = None,
        preserve_generation: bool = False,
        timeout: _Timeout = 60,
        if_generation_match: Collection[int | None] | None = None,
        if_generation_not_match: Collection[int | None] | None = None,
        if_metageneration_match: Collection[int | None] | None = None,
        if_metageneration_not_match: Collection[int | None] | None = None,
        retry: _Retry = ...,
    ) -> None: ...
    def copy_blob(
        self,
        blob: Blob,
        destination_bucket: Bucket,
        new_name: str | None = None,
        client: Client | None = None,
        preserve_acl: bool = True,  # deprecated; `False` clears the copy's ACL with an extra request
        source_generation: int | None = None,
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
        destination_contexts: ObjectContexts | None = None,  # the docstring says "or dict", but a dict raises
    ) -> Blob: ...
    def rename_blob(
        self,
        blob: Blob,
        new_name: str,
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
    ) -> Blob: ...
    def move_blob(
        self,
        blob: Blob,
        new_name: str,
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
    ) -> Blob: ...
    def restore_blob(
        self,
        blob_name: str,
        client: Client | None = None,
        generation: int | None = None,
        copy_source_acl: bool | None = None,
        projection: str | None = None,
        if_generation_match: int | None = None,
        if_generation_not_match: int | None = None,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
    ) -> Blob: ...
    # copies of the bucket's entries: change the list, then assign it back
    @property
    def cors(self) -> list[CorsPolicy]: ...
    @cors.setter
    def cors(self, entries: Sequence[CorsPolicy]) -> None: ...
    @property
    def encryption(self) -> BucketEncryption: ...
    @encryption.setter
    def encryption(self, value: BucketEncryption | Mapping[str, object]) -> None: ...
    # a copy, like `cors`; keys left out of the assigned mapping are removed on the next `patch()`
    @property
    def labels(self) -> dict[str, str]: ...
    @labels.setter
    def labels(self, mapping: Mapping[str, str]) -> None: ...
    @property
    def etag(self) -> str | None: ...
    @property
    def id(self) -> str | None: ...
    @property
    def iam_configuration(self) -> IAMConfiguration: ...
    @property
    def soft_delete_policy(self) -> SoftDeletePolicy: ...
    # A generator of copies of the bucket's rules; rules of an unknown action type are skipped with a warning.
    # Assign the changed rules back (any mappings, such as the `LifecycleRule*` classes).
    @property
    def lifecycle_rules(
        self,
    ) -> Iterator[LifecycleRuleDelete | LifecycleRuleSetStorageClass | LifecycleRuleAbortIncompleteMultipartUpload]: ...
    @lifecycle_rules.setter
    def lifecycle_rules(self, rules: Iterable[Mapping[str, object]]) -> None: ...
    def clear_lifecycle_rules(self) -> None: ...
    def add_lifecycle_delete_rule(self, **kw: Unpack[_LifecycleRuleConditionsKwargs]) -> None: ...
    def add_lifecycle_set_storage_class_rule(
        self, storage_class: str, **kw: Unpack[_LifecycleRuleConditionsKwargs]
    ) -> None: ...
    def add_lifecycle_abort_incomplete_multipart_upload_rule(
        self, **kw: Unpack[_AbortIncompleteMultipartUploadKwargs]
    ) -> None: ...
    @property
    def location(self) -> str | None: ...
    @location.setter
    @deprecated("Pass the location to Bucket.create() instead.")
    def location(self, value: str) -> None: ...
    # set only for custom dual-region buckets
    @property
    def data_locations(self) -> list[str] | None: ...
    @property
    def location_type(self) -> str | None: ...
    # `None` if logging is disabled
    def get_logging(self) -> _Logging | None: ...
    def enable_logging(self, bucket_name: str, object_prefix: str = "") -> None: ...
    def disable_logging(self) -> None: ...
    @property
    def metageneration(self) -> int | None: ...
    @property
    def owner(self) -> _Owner | None: ...
    @property
    def project_number(self) -> int | None: ...
    @property
    def retention_policy_effective_time(self) -> datetime | None: ...
    @property
    def retention_policy_locked(self) -> bool | None: ...
    # in seconds; `None` removes the retention policy
    @property
    def retention_period(self) -> int | None: ...
    @retention_period.setter
    def retention_period(self, value: int | None) -> None: ...
    @property
    def self_link(self) -> str | None: ...
    # one of `STORAGE_CLASSES`
    @property
    def storage_class(self) -> str | None: ...
    @storage_class.setter
    def storage_class(self, value: str) -> None: ...
    @property
    def time_created(self) -> datetime | None: ...
    @property
    def updated(self) -> datetime | None: ...
    @property
    def autoclass_toggle_time(self) -> datetime | None: ...
    # "NEARLINE" or "ARCHIVE"
    @property
    def autoclass_terminal_storage_class(self) -> str | None: ...
    @autoclass_terminal_storage_class.setter
    def autoclass_terminal_storage_class(self, value: str) -> None: ...
    @property
    def autoclass_terminal_storage_class_update_time(self) -> datetime | None: ...
    @property
    def object_retention_mode(self) -> str | None: ...
    # can only be set before the bucket is created
    @property
    def hierarchical_namespace_enabled(self) -> bool | None: ...
    @hierarchical_namespace_enabled.setter
    def hierarchical_namespace_enabled(self, value: bool) -> None: ...
    def configure_website(self, main_page_suffix: str | None = None, not_found_page: str | None = None) -> None: ...
    def disable_website(self) -> None: ...
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
    # returns the subset of `permissions` the caller has
    def test_iam_permissions(
        self,
        permissions: Sequence[str],
        client: Client | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
    ) -> list[str]: ...
    def make_public(
        self,
        recursive: bool = False,
        future: bool = False,
        client: Client | None = None,
        timeout: _Timeout = 60,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        retry: _Retry = ...,
    ) -> None: ...
    def make_private(
        self,
        recursive: bool = False,
        future: bool = False,
        client: Client | None = None,
        timeout: _Timeout = 60,
        if_metageneration_match: int | None = None,
        if_metageneration_not_match: int | None = None,
        retry: _Retry = ...,
    ) -> None: ...
    # the V2 policy document; `Client.generate_signed_post_policy_v4` makes the V4 one
    def generate_upload_policy(
        self,
        conditions: list[PostPolicyCondition],
        expiration: datetime | None = None,  # in UTC; `None`: an hour from now
        client: Client | None = None,
    ) -> _UploadPolicyFields: ...
    # raises `ValueError` unless the bucket is loaded and has an unlocked retention policy
    def lock_retention_policy(
        self,
        client: Client | None = None,
        timeout: _Timeout = 60,
        retry: _Retry = ...,
    ) -> None: ...
    def generate_signed_url(
        self,
        expiration: int | datetime | timedelta | None = None,
        api_access_endpoint: str | None = None,
        method: str = "GET",
        headers: dict[str, str] | None = None,  # a `dict`: the signed headers (`Host`, ...) are added to it
        query_parameters: Mapping[str, str] | None = None,
        client: Client | None = None,
        credentials: Credentials | None = None,
        version: Literal["v2", "v4"] | None = None,
        virtual_hosted_style: bool = False,
        bucket_bound_hostname: str | None = None,
        scheme: str = "http",
    ) -> str: ...
    # a new `IPFilter` each time, so changing it has no effect: assign one back instead
    @property
    def ip_filter(self) -> IPFilter | None: ...
    @ip_filter.setter
    def ip_filter(self, value: IPFilter | Mapping[str, object] | None) -> None: ...
