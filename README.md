# types-google-cloud-storage

Partial typing stubs for [`google-cloud-storage`](https://pypi.org/project/google-cloud-storage/), which ships no
type information of its own. Without them, pyright and mypy report the import as missing stubs, and every parameter
of `Client`, `Bucket` and `Blob` as `Unknown`. [typeshed](https://github.com/python/typeshed) has no stubs
for this library.

The stubs are checked against the runtime library with mypy's `stubtest`; [Versions](#versions) lists the
`google-cloud-storage` version each release was checked against.

## Install

Releases are published to the Agnos package index at `https://pkgs.agnos.one/simple/`.

Install with [uv](https://docs.astral.sh/uv/):

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

The package has no runtime code: install `google-cloud-storage` itself as a regular dependency. It requires Python
3.14 or later.

## What's covered

The stubs cover `Client`, `Bucket` and `Blob` and the modules around them. Every stubbed method has the library's
full signature, so all its parameters can be passed, positionally or by keyword, as at runtime.

| Module | Stubbed |
| --- | --- |
| `.client`, `.bucket`, `.blob` | `Client`, `Bucket`, `Blob` and their helper classes, except ACLs, notifications and HMAC keys |
| `.fileio`, `.batch`, `.transfer_manager` | `BlobReader` / `BlobWriter` (for `Blob.open`), `Batch`, the transfer functions |
| `.retry`, `.ip_filter`, `.constants`, `.exceptions` | all (in `.exceptions`, the exception classes) |

Not stubbed yet: the `acl`, `notification` and `hmac_key` modules and the members that use them (`Bucket.acl`,
`Bucket.notification`, `Client.list_hmac_keys`, and so on), the `iam`, `grpc_client` and `version` modules, the
deprecated `Blob.download_as_string`, and `Bucket.clear_lifecyle_rules`, a misspelled alias. The package is marked
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

- **Some names exist only in the stubs**, for annotations: the iterators `list_blobs` and `list_buckets` return
  (`BlobIterator`, `BucketIterator`) and their pages, `TypedDict`s for typing the `transfer_manager` kwargs, and
  `CorsPolicy`, `PostPolicyCondition` and `ClientOptionsDict` for values that callers build. Import them under
  `if TYPE_CHECKING:`.
- **Some arguments must be a `dict`, not any mapping**, because the library writes to them: `headers` of
  `generate_signed_url` gets the signed headers added, and `client_options` given as a dict gets `api_key`.
- **`Blob.open` needs a literal mode.** Its overloads return `TextIOWrapper` for `"r"` / `"rt"` / `"w"` / `"wt"`,
  `BlobReader` for `"rb"` and `BlobWriter` for `"wb"`, and reject the other modes, which raise at runtime. A mode held
  in a `str` variable has to be narrowed to one of those literals first.
- **Deprecated members are marked `@deprecated`**, such as `Bucket.from_string` and the `Bucket.location` setter, so
  pyright strict reports their use (`reportDeprecated`).
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
| 0.2.0 | 3.17.2 |
| 0.3.0 | 3.17.2 |
