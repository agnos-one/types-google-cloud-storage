# Type-checked by pyright, never run. Only for what the stubs don't spell out: how the package resolves imports,
# `**kwargs`, the stub-only names, and that realistic calls are accepted. Don't restate single annotations here.
from datetime import timedelta
from typing import TYPE_CHECKING, assert_type

import google.api_core.exceptions
from google.cloud import exceptions, storage
from google.cloud.storage.retry import DEFAULT_RETRY

if TYPE_CHECKING:
    # stub-only: they don't exist at runtime
    from google.cloud.storage.bucket import BlobIterator, BlobPage


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
