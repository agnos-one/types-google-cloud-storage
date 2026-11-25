# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-11-25

First release, under the MIT License, published to the package index at `https://pkgs.agnos.one/simple/`. Checked
with `stubtest` against `google-cloud-storage` 3.17.2.

### Added

- Partial PEP 561 stubs for `google.cloud.storage`: `Client`, `Bucket`, `Blob` and the `retry` module.
- `Client`: constructor, `bucket()`, `get_bucket()`, `lookup_bucket()` and `list_blobs()`.
- `Bucket`: constructor, `blob()`, `exists()`, `get_blob()`, `list_blobs()` and `delete_blob()`.
- `Blob`: constructor, metadata properties, `exists()`, `reload()`, `patch()`, `delete()`, the `download_*` and
  `upload_from_*` methods, and `generate_signed_url()`.
- `BlobIterator`, a stub-only type for what `list_blobs()` returns: an iterator of `Blob` with `prefixes` and
  `pages`, an iterator of the stub-only `BlobPage`.
- Every stubbed method has the library's full signature, with no `Any`.

[Unreleased]: https://github.com/agnos-one/types-google-cloud-storage/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/agnos-one/types-google-cloud-storage/releases/tag/v0.1.0
