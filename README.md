# types-google-cloud-storage

Partial typing stubs for [`google-cloud-storage`](https://pypi.org/project/google-cloud-storage/), which ships no
type information of its own. Without them, pyright, mypy reports the import as missing stubs, and every parameter of
`Client`, `Bucket` and `Blob` as `Unknown`. [typeshed](https://github.com/python/typeshed) has no stubs
for this library.

The stubs are checked against the runtime library with mypy's `stubtest`; [Versions](#versions) lists the
`google-cloud-storage` version each release was checked against.

## Install

Releases are published to the Agnos package index at `https://pkgs.agnos.one/simple/`, not PyPI. With uv:

```toml
# pyproject.toml
[[tool.uv.index]]
name = "agnos"
url = "https://pkgs.agnos.one/simple/"
explicit = true

[tool.uv.sources]
types-google-cloud-storage = { index = "agnos" }
```

```bash
uv add --dev types-google-cloud-storage
```

The package has no runtime code: install `google-cloud-storage` itself as a regular dependency.

## What's covered

The stubs cover the core object API. Every stubbed method has the library's full signature, so all its parameters
can be passed, positionally or by keyword, as at runtime.

| Module | Stubbed |
| --- | --- |
| `google.cloud.storage` | `Client`, `Bucket`, `Blob`, `__version__` |
| `.client` | `Client`: constructor, `bucket`, `get_bucket`, `lookup_bucket`, `list_blobs` |
| `.bucket` | `Bucket`: constructor, `name`, `client`, `user_project`, `path`, `blob`, `exists`, `get_blob`, `list_blobs`, `delete_blob`; `BlobIterator`, `BlobPage` (stub-only, see [Notes](#notes)) |
| `.blob` | `Blob`: constructor, metadata properties (`size`, `updated`, `content_type`, `metadata`, ...), `exists`, `reload`, `patch`, `delete`, `download_as_bytes`, `download_as_text`, `download_to_filename`, `upload_from_string`, `upload_from_file`, `upload_from_filename`, `generate_signed_url` |
| `.retry` | `DEFAULT_RETRY`, `ConditionalRetryPolicy`, the `DEFAULT_RETRY_IF_*` policies |

Anything else (`Batch`, ACLs, bucket configuration, `copy_blob`, ...) is not stubbed yet. The package is marked
`partial` (PEP 561), so modules it doesn't stub, such as `google.cloud.exceptions`, still resolve to the installed
libraries.

```python
from datetime import timedelta

from google.cloud import storage

client = storage.Client()
blob = client.bucket("my-bucket").blob("reports/2026-11.pdf")
blob.upload_from_string(data, content_type="application/pdf")  # data: bytes | str
url = blob.generate_signed_url(expiration=timedelta(minutes=15), version="v4")  # str

for item in client.list_blobs("my-bucket", prefix="reports/"):  # Blob
    print(item.name, item.size, item.updated)  # str, int | None, datetime | None
```

## Notes

- **`BlobIterator` and `BlobPage` exist only in the stubs.** `list_blobs` returns a `BlobIterator`, typed as an
  iterator of `Blob` with `prefixes`, `next_page_token`, `num_results` and `pages` (an iterator of `BlobPage`, each
  an iterator of `Blob`); at runtime they are an `HTTPIterator` and its `Page`s from `google-api-core`. To annotate
  with them, import them under `if TYPE_CHECKING:` from `google.cloud.storage.bucket`.
- **Metadata properties are `None` until loaded.** A `Blob` from `bucket.blob(...)` has no metadata until
  `reload()`; those from `get_blob` and `list_blobs` do.
- **`Bucket.name` and `Blob.name` are `str`**, though the library technically allows `None`: in practice they are
  always set.

## Versions

The stubs have their own version numbers, which don't follow `google-cloud-storage`'s. Each release is checked with
`stubtest` against one `google-cloud-storage` version. Other versions usually work as well, as long as the stubbed
signatures haven't changed.

| Stubs | Checked against `google-cloud-storage` |
| --- | --- |
| 0.1.0 | 3.17.2 |
