# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-11-25

Checked with `stubtest` against `google-cloud-storage` 3.17.2.

### Added

- `Client`: every remaining member except the HMAC key methods, including `create_bucket()`, `list_buckets()`,
  `restore_bucket()`, `download_blob_to_file()`, `batch()`, `generate_signed_post_policy_v4()`, the
  `from_service_account_*()` factories and use as a context manager.
- `Bucket`: every remaining member except `acl`, `default_object_acl`, the notification methods and the misspelled
  `clear_lifecyle_rules` alias, including all properties, `create()`, `delete()`, `update()`, `copy_blob()`,
  `rename_blob()`, `move_blob()`, `restore_blob()`, `delete_blobs()`, the lifecycle rule, logging and website
  helpers, IAM, `generate_signed_url()` and `generate_upload_policy()`, and the configuration classes
  `IAMConfiguration`, `SoftDeletePolicy`, `BucketEncryption`, `EncryptionEnforcementConfig`,
  `LifecycleRuleConditions` and the `LifecycleRule*` rules.
- `Blob`: every remaining member except `acl`, including all properties, `open()` (overloaded by mode), `compose()`,
  `rewrite()`, `update_storage_class()`, `download_to_file()`, `create_resumable_upload_session()` and IAM, and the
  `Retention`, `ObjectContexts` and `ObjectCustomContextPayload` classes.
- New modules: `fileio` (`BlobReader`, `BlobWriter`), `batch` (`Batch`, also exported from `google.cloud.storage`),
  `transfer_manager`, `ip_filter`, `constants` and `exceptions`; the `is_*` predicates in `retry`.
- Stub-only types: `BucketIterator` and `BucketPage` for `list_buckets()`, `CorsPolicy`, `PostPolicyCondition`,
  `SignedPostPolicyV4`, and `TypedDict`s for the `transfer_manager` keyword dicts.

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

[Unreleased]: https://github.com/agnos-one/types-google-cloud-storage/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/agnos-one/types-google-cloud-storage/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/agnos-one/types-google-cloud-storage/releases/tag/v0.1.0
