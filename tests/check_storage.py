# Type-checked by pyright, never run. Only for what the stubs don't spell out: how the package resolves imports,
# `**kwargs`, the stub-only names, and that realistic calls are accepted. Don't restate single annotations here.
from datetime import UTC, date, datetime, timedelta
from io import TextIOWrapper
from typing import TYPE_CHECKING, assert_type

import google.api_core.exceptions
from google.cloud import exceptions, storage
from google.cloud.storage import transfer_manager
from google.cloud.storage.bucket import LifecycleRuleDelete, LifecycleRuleSetStorageClass, SoftDeletePolicy
from google.cloud.storage.fileio import BlobReader, BlobWriter
from google.cloud.storage.ip_filter import IPFilter, PublicNetworkSource
from google.cloud.storage.retry import DEFAULT_RETRY

if TYPE_CHECKING:
    # stub-only: they don't exist at runtime
    from google.cloud.storage.bucket import BlobIterator, BlobPage, CorsPolicy
    from google.cloud.storage.client import BucketPage, PostPolicyCondition, SignedPostPolicyV4
    from google.cloud.storage.transfer_manager import UploadKwargs


def check_imports() -> None:
    # `from google.cloud import storage` above needs the empty `cloud/__init__.pyi`; the modules not stubbed here
    # resolve to the installed libraries, as py.typed marks the stubs partial
    assert_type(exceptions.NotFound(""), exceptions.NotFound)
    assert_type(google.api_core.exceptions.Conflict(""), google.api_core.exceptions.Conflict)


# annotations aren't evaluated at runtime (PEP 649), so the imports can stay under TYPE_CHECKING
def list_folders(bucket: storage.Bucket) -> BlobIterator:
    return bucket.list_blobs(delimiter="/")


def blob_names(page: BlobPage) -> list[str]:
    return [blob.name for blob in page]


def check_blob_iterator(client: storage.Client) -> None:
    blobs = client.list_blobs("bucket", prefix="a/", delimiter="/")
    assert_type(blobs, "BlobIterator")  # quoted: the name exists only for type checkers
    for blob in blobs:
        assert_type(blob, storage.Blob)


def check_blob_pages(bucket: storage.Bucket) -> None:
    for page in bucket.list_blobs(page_size=100).pages:
        assert_type(page, "BlobPage")
        for blob in page:
            assert_type(blob, storage.Blob)


def check_get_blob_kwargs(bucket: storage.Bucket) -> None:
    # `**kwargs` takes the `Blob` constructor arguments only (`Unpack[_BlobKwargs]`)
    bucket.get_blob("a/b.txt", chunk_size=256 * 1024, kms_key_name="key")
    bucket.get_blob("a/b.txt", content_type="text/plain")  # pyright: ignore[reportCallIssue]


def check_calls(client: storage.Client, blob: storage.Blob) -> None:
    client.get_bucket("bucket", timeout=(3, 10), retry=None)
    blob.metadata = {"key": "value", "obsolete": None}  # the setter takes a Mapping; `None` deletes a key
    blob.upload_from_string(b"data", content_type="application/pdf", retry=DEFAULT_RETRY, if_generation_match=0)
    blob.generate_signed_url(expiration=timedelta(minutes=5), method="PUT", version="v4")


def check_blob_open(blob: storage.Blob) -> None:
    # the overloads pick the return type from the mode
    assert_type(blob.open(), TextIOWrapper)
    assert_type(blob.open("rt", encoding="utf-8"), TextIOWrapper)
    assert_type(blob.open("w", newline=""), TextIOWrapper)
    assert_type(blob.open("rb"), BlobReader)
    assert_type(blob.open("wb", ignore_flush=True), BlobWriter)
    with blob.open("rb") as reader:
        assert_type(reader, BlobReader)
    # The runtime raises for other modes, and for arguments the mode doesn't take. When no overload matches,
    # pyright reports the call (reportCallIssue) and the argument of the last overload (reportArgumentType).
    blob.open("a")  # pyright: ignore[reportCallIssue, reportArgumentType]
    blob.open("rb", encoding="utf-8")  # pyright: ignore[reportCallIssue, reportArgumentType]
    blob.open("r", ignore_flush=True)  # pyright: ignore[reportCallIssue, reportArgumentType]
    blob.open("w", ignore_flush=False)  # pyright: ignore[reportCallIssue, reportArgumentType]


def check_blob_open_kwargs(blob: storage.Blob) -> None:
    # `**kwargs` takes the download arguments in the read modes and the upload arguments in the write modes
    blob.open("rb", chunk_size=256 * 1024, raw_download=True, timeout=(3, 10), retry=DEFAULT_RETRY)
    blob.open("w", content_type="text/csv", if_generation_match=0, checksum="crc32c")
    blob.open("r", content_type="text/csv")  # pyright: ignore[reportCallIssue, reportArgumentType]
    blob.open("wb", raw_download=True)  # pyright: ignore[reportCallIssue, reportArgumentType]
    # `BlobReader` and `BlobWriter` take `retry` as a parameter of its own
    BlobReader(blob, retry=None, single_shot_download=True)
    BlobWriter(blob, ignore_flush=True, predefined_acl="private", timeout=60)
    BlobWriter(blob, raw_download=True)  # pyright: ignore[reportCallIssue]


def check_blob_calls(bucket: storage.Bucket, blob: storage.Blob) -> None:
    sources = [bucket.blob("a"), bucket.blob("b")]
    blob.compose(sources, if_generation_match=0, if_source_generation_match=[1, None])
    token, _, _ = blob.rewrite(sources[0])
    while token is not None:
        token, _, _ = blob.rewrite(sources[0], token=token)
    blob.contexts = {"custom": {"team": {"value": "storage"}}}
    # a typed variable is accepted too, not only a literal (the setter takes `Mapping`s)
    contexts: dict[str, dict[str, dict[str, str]]] = {"custom": {"team": {"value": "storage"}}}
    blob.contexts = contexts
    blob.retention.retain_until_time = datetime(2030, 1, 1, tzinfo=UTC)
    blob.custom_time = None


def cors_policy(origin: str) -> CorsPolicy:
    return {"origin": [origin], "method": ["GET", "PUT"], "maxAgeSeconds": 3600}


def check_cors(bucket: storage.Bucket) -> None:
    policies = bucket.cors
    assert_type(policies, "list[CorsPolicy]")
    policies.append(cors_policy("https://example.com"))
    bucket.cors = policies
    bucket.cors = [{"origin": ["*"], "max_age": 60}]  # pyright: ignore[reportAttributeAccessIssue]


def check_lifecycle_kwargs(bucket: storage.Bucket) -> None:
    # the rule helpers take the `LifecycleRuleConditions` arguments through `**kw` (`Unpack[...]`)
    bucket.add_lifecycle_delete_rule(age=30, matches_prefix=["tmp/"])
    bucket.add_lifecycle_set_storage_class_rule("COLDLINE", created_before=date(2026, 1, 1))
    bucket.add_lifecycle_delete_rule(max_age=30)  # pyright: ignore[reportCallIssue]
    # `age` is the only condition of the abort-incomplete-upload rule
    bucket.add_lifecycle_abort_incomplete_multipart_upload_rule(age=7)
    bucket.add_lifecycle_abort_incomplete_multipart_upload_rule(matches_prefix=["x"])  # pyright: ignore[reportCallIssue]
    # the setter takes the rule classes and the rules read back alike
    bucket.lifecycle_rules = [
        *bucket.lifecycle_rules,
        LifecycleRuleDelete(number_of_newer_versions=3, is_live=False),
        LifecycleRuleSetStorageClass("ARCHIVE", age=365),
    ]


def check_soft_delete_policy_kwargs(bucket: storage.Bucket) -> None:
    SoftDeletePolicy(bucket, retention_duration_seconds=7 * 24 * 3600)
    SoftDeletePolicy(bucket, retention_days=7)  # pyright: ignore[reportCallIssue]


def check_delete_blobs(bucket: storage.Bucket, blobs: list[storage.Blob], names: list[str]) -> None:
    # generic: `on_error` gets the items of `blobs`, whichever of `Blob` and `str` they are
    def on_missing_blob(blob: storage.Blob) -> None: ...
    def on_missing_name(name: str) -> None: ...

    bucket.delete_blobs(blobs, on_error=on_missing_blob, if_generation_match=[blob.generation for blob in blobs])
    bucket.delete_blobs(names, on_error=on_missing_name)
    bucket.delete_blobs(names, on_error=on_missing_blob)  # pyright: ignore[reportArgumentType]


class MyBucket(storage.Bucket): ...


def check_from_uri(client: storage.Client) -> None:
    assert_type(MyBucket.from_uri("gs://bucket", client=client), MyBucket)


def check_bucket_calls(client: storage.Client, bucket: storage.Bucket, blob: storage.Blob) -> None:
    bucket.labels = {"env": "prod"}
    bucket.retention_period = None
    ip_filter = IPFilter()
    ip_filter.mode = "Enabled"
    ip_filter.public_network_source = PublicNetworkSource(allowed_ip_cidr_ranges=["203.0.113.5/32"])
    bucket.ip_filter = ip_filter
    bucket.patch(if_metageneration_match=bucket.metageneration, retry=DEFAULT_RETRY)
    policy = bucket.get_iam_policy(requested_policy_version=3, timeout=(3, 10))
    bucket.set_iam_policy(policy)
    bucket.copy_blob(blob, client.bucket("backup"), new_name="a/b.txt", if_generation_match=0)
    bucket.generate_signed_url(expiration=timedelta(hours=1), version="v4", virtual_hosted_style=True)


class MyClient(storage.Client): ...


def check_client_factories(info: dict[str, str]) -> None:
    # the factories return `Self`, and take the constructor's keyword arguments other than `credentials`
    assert_type(MyClient.create_anonymous_client(), MyClient)
    assert_type(MyClient.from_service_account_info(info, project="p"), MyClient)
    storage.Client.from_service_account_json("key.json", client_options={"api_endpoint": "http://localhost:4443"})
    storage.Client.from_service_account_info(info, credentials=None)  # pyright: ignore[reportCallIssue]
    storage.Client.from_service_account_info(info, "project")  # pyright: ignore[reportArgumentType]


def bucket_names(page: BucketPage) -> list[str]:
    return [bucket.name for bucket in page]


def check_bucket_pages(client: storage.Client) -> None:
    for page in client.list_buckets(prefix="logs-", return_partial_success=True).pages:
        assert_type(page, "BucketPage")
        for bucket in page:
            assert_type(bucket, storage.Bucket)


def post_policy(client: storage.Client) -> SignedPostPolicyV4:
    return client.generate_signed_post_policy_v4(
        "bucket",
        "uploads/a.txt",
        expiration=timedelta(minutes=10),
        conditions=[["starts-with", "$key", "uploads/"], ["content-length-range", 0, 1024], {"acl": "private"}],
        fields={"acl": "private"},
    )


def post_policy_conditions(client: storage.Client, bucket: storage.Bucket, prefix: str) -> None:
    # a list built in a variable needs the stub-only element type: the parameter is a (mutable, invariant) `list`
    conditions: list[PostPolicyCondition] = [["starts-with", "$key", prefix]]
    client.generate_signed_post_policy_v4("bucket", f"{prefix}a.txt", expiration=None, conditions=conditions)
    bucket.generate_upload_policy(conditions)


def check_batch(client: storage.Client, bucket: storage.Bucket) -> None:
    with client.batch(raise_exception=False) as batch:
        assert_type(batch, storage.Batch)
        bucket.delete_blob("a.txt")


def check_transfer_manager(bucket: storage.Bucket, blob: storage.Blob) -> None:
    # the `*_kwargs` dicts are TypedDicts: a literal is checked against the keys, a variable needs the annotation
    upload_kwargs: UploadKwargs = {"content_type": "text/plain", "timeout": (3, 10)}
    transfer_manager.upload_many_from_filenames(bucket, ["a.txt"], source_directory="/tmp", upload_kwargs=upload_kwargs)
    transfer_manager.download_many(
        [(blob, "a.txt")], download_kwargs={"raw_download": True}, worker_type=transfer_manager.THREAD
    )
    transfer_manager.download_many([(blob, "a.txt")], worker_type="fork")  # pyright: ignore[reportArgumentType]
    transfer_manager.download_chunks_concurrently(blob, "a.bin", download_kwargs={"retry": DEFAULT_RETRY})
    transfer_manager.download_chunks_concurrently(
        blob,
        "a.bin",
        download_kwargs={"checksum": "md5"},  # pyright: ignore[reportArgumentType]
    )
