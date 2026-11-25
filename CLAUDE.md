# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`types-google-cloud-storage` is a stub-only PEP 561 package: partial typing stubs for `google-cloud-storage`, which
ships no type information. It has no runtime code. `README.md` lists what is covered and how consumers install it.

## Commands

```bash
uv sync                  # install; the project itself goes in editable, so pyright sees src/
uv run ruff format
uv run ruff check
uv run pyright           # strict; checks the stubs and the type-checking cases in tests/

# Compare the stubs with the installed google-cloud-storage
uv run --no-editable --reinstall-package types-google-cloud-storage \
  stubtest google.cloud.storage --ignore-missing-stub --allowlist tests/allowlist.txt
uv sync --reinstall-package types-google-cloud-storage   # back to the editable install afterwards

uv build                 # dist/: the wheel holds only google-stubs/
npx markdownlint-cli2 "**/*.md"
```

ruff, pyright, stubtest and markdownlint must all report no issues before a commit.

- `stubtest` needs the package installed for real: mypy can't read the editable install's `src/google-stubs`.
`--reinstall-package` matters too: without it uv reuses its cached build of the same version, and stubtest checks
stale stubs.
- `--ignore-missing-stub` is what makes the stubs partial: stubtest skips runtime names the stubs leave out, but
  everything that is stubbed must match the runtime.

## Layout

```text
src/google-stubs/
├── py.typed             # "partial": modules not stubbed here fall back to the installed libraries
└── cloud/
    ├── __init__.pyi     # empty; see below
    └── storage/         # __init__, client, bucket, blob, fileio, batch, transfer_manager, ip_filter, retry,
                         # constants, exceptions
tests/
├── check_storage.py     # type-checking cases (imports, kwargs, stub-only names), never run
└── allowlist.txt        # stub-only names stubtest would report as missing at runtime
scripts/build_index.py   # writes the package index pages; used by the release workflow
.github/workflows/release.yml
```

`google.cloud` is a namespace package at runtime, but without `cloud/__init__.pyi` pyright reports
`from google.cloud import storage` as `Stub file not found for "google.cloud"`. Keep it empty.

`pyproject.toml` builds `google-stubs` with `uv_build`'s `namespace = true`, as `google-stubs/` has no
`__init__.pyi`. The runtime dependencies are `google-api-core` and `google-auth`, because the stubs import their
types (`Retry`, `Policy`, `ClientInfo`, `ClientOptions`, `Credentials`); `google-cloud-storage` itself is only a dev
dependency, pinned to the version the stubs are checked against.

## Writing stubs

- **Signatures: copy them from the runtime, completely**: every parameter, in the runtime's order and kind; don't
  drop any or add `*` (stubtest enforces this). Print them with
  `uv run python -I -c "import inspect; from google.cloud.storage import Blob; print(inspect.signature(Blob.reload))"`.
- **Types come from the docstrings and the code**, not guesses. For example, the docstring types `if_etag_match` as
  `Union[str, Set[str]]`, but the code joins any iterable, so the stub has `str | Iterable[str]`.
  - Parameters take read-only types (`Mapping`, `Sequence`): `dict` and `list` are invariant, so a parameter typed
    `dict[str, str | None]` rejects a caller's `dict[str, str]` variable, while `Mapping[str, str | None]` accepts
    it. Prefer `Sequence` to `Iterable` where the runtime takes `len()` or may iterate twice: a generator would be
    empty when a request is retried.
  - Where the runtime mutates the value, the parameter has to be a `list` or `dict`. Callers must then annotate
    their variable with exactly the element type, so give it a public stub-only name. For example,
    `generate_signed_post_policy_v4` appends to `conditions`, so the parameter is `list[PostPolicyCondition]`, and
    callers write `conditions: list[PostPolicyCondition] = [...]`.
  - JSON-backed properties (`size`, `content_type`, ...) return `X | None`, as they are `None` until loaded, unless
    the code defaults them: `requester_pays` reads `False` when the field is missing, so it is `bool`.
  - No `Any`: `**kwargs` is `Unpack[TypedDict]` of the keys the code accepts (see `_BlobKwargs` for
    `Bucket.get_blob`). A type from an untyped library is `object` with a comment: `Client(_http=...)` takes a
    `requests.Session`, so it is `_http: object | None = None  # a requests.Session`.
- **Defaults:** literal defaults as they are (`timeout: _Timeout = 60`, `projection: str = "noAcl"`), `...` for the
  rest: objects, sentinels and mutable defaults (`retry: _Retry = ...` for `retry=DEFAULT_RETRY`).
- **Private aliases (`_Timeout`, `_Retry`, ...) are redefined in each module**: `from ...blob import _Timeout` in
  `bucket.pyi` is `reportPrivateUsage` in pyright, and a public `Timeout` would be reported by stubtest as missing at
  runtime.
- **Stub-only public names** need a `tests/allowlist.txt` entry and a comment saying they don't exist at runtime:
  `list_blobs` returns a `BlobIterator` in the stubs, but an untyped `HTTPIterator` at runtime. A `TypedDict` for a
  value callers build in a variable is public: `kwargs = {"timeout": 30}` is inferred as `dict[str, int]`, which an
  `upload_kwargs: UploadKwargs` parameter rejects, so callers need the name to write `kwargs: UploadKwargs = ...`.
  One only for `**kwargs` or a return value stays private (`_BlobKwargs`).
- **Deprecated members** (a runtime warning, or "deprecated" in the docstring) get `@deprecated` from `warnings`, so
  pyright strict reports a call to `Bucket.from_string`; deprecated parameters get a comment.
- **No suppressions**, except `# type: ignore[override]` with a comment where the runtime really narrows its base
  class: `BufferedIOBase.read` accepts `size=None`, but `BlobReader.read` raises on it, so its stub is
  `def read(self, size: int = -1)` with the ignore.
- **Tests: only what the stubs don't spell out**, as stubtest checks the signatures: no
  `assert_type(blob.size, int | None)`, which only restates the stub. `tests/check_storage.py` covers:
  - import resolution: the empty `cloud/__init__.pyi`, and the `partial` fallback to unstubbed modules
  - what callers get from `Unpack` kwargs, overloads and generics (`blob.open("rb")` returns a `BlobReader`)
  - stub-only names, imported under `if TYPE_CHECKING:` and used in annotations
  - a few realistic calls, to show the types accept real values (`timeout=(3, 10)`, `retry=DEFAULT_RETRY`)

  A call the stubs must reject is written with a rule-specific ignore, such as
  `bucket.get_blob("a", content_type="x")  # pyright: ignore[reportCallIssue]`. `reportUnnecessaryTypeIgnoreComment`
  is an error, so the check fails if the stubs start accepting the call.
- **README:** when adding a module or leaving members out, update the coverage table and "Not stubbed yet".

## Versions

The package has its own semantic version, independent of `google-cloud-storage`'s; it is not updated
for every `google-cloud-storage` release. The dev pin (`google-cloud-storage==X.Y.Z`) is the version stubtest
checks against, and the Versions table in `README.md` maps each release to it.

## Release

Releases go to the static PEP 503 index at `https://pkgs.agnos.one/simple/`, through `.github/workflows/release.yml`.
To release:

1. To check against a newer `google-cloud-storage`, bump the dev pin, `uv sync`, and update the stubs until
   stubtest passes.
2. Bump the version: `uv version --bump minor` for new stubs or changed types, `--bump patch` for fixes.
3. Add a row to the Versions table in `README.md`: the new version and the dev pin.
4. In `CHANGELOG.md`, move the `Unreleased` entries into a dated `## [X.Y.Z] - YYYY-MM-DD` section and update the
   links at the bottom.
5. Commit and push, then `git tag vX.Y.Z && git push origin vX.Y.Z`.

The workflow fails unless the tag is exactly `v` + the `pyproject.toml` version and the changelog section is dated.
It runs ruff, pyright and stubtest (not markdownlint), builds with `uv build --no-sources`, checks the files with
`twine check`, uploads them and rebuilds the project and root index pages in the R2 bucket, then creates a GitHub
Release from the changelog section and posts the result to Slack. It refuses to overwrite a published version, so a
bad release is fixed by publishing a new version.

The `publish` job runs in the `agnos-packages` environment, which only `v*` tags may deploy to. The R2 secrets
(`R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ACCOUNT_ID`, `R2_BUCKET`) are set on that environment;
`SLACK_WEBHOOK_URL` is an organization secret.

`scripts/build_index.py` writes the index pages with the standard library only, so it runs on the runner's system
Python. Keep it in sync with the copy in `keycloak-auth`: both rewrite the shared root index.
