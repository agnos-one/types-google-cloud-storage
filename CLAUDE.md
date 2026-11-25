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
    └── storage/         # __init__, client, bucket, blob, retry
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
types (`Retry`, `ClientInfo`, `ClientOptions`, `Credentials`); `google-cloud-storage` itself is only a dev
dependency, pinned to the version the stubs are checked against.

## Writing stubs

- **Copy signatures from the runtime, completely.** A stubbed method lists every parameter, in the runtime's order
  and kind (positional-or-keyword, keyword-only, `**kwargs`); don't drop parameters or add `*`. stubtest enforces
  this. Print the signatures with
  `uv run python -I -c "import inspect; from google.cloud.storage import Blob; print(inspect.signature(Blob.reload))"`.
- **Types come from the docstrings and the code**, not guesses: e.g. `if_etag_match` is `str | Iterable[str]`,
  `checksum` is `Literal["md5", "crc32c", "auto"] | None`. Precondition parameters are `int | None`.
- **Defaults:** write literal defaults (`None`, `60`, `"noAcl"`, `False`) as they are, and `...` for the rest
  (`retry=DEFAULT_RETRY`, sentinels, mutable defaults).
- **No `Any`.** For `**kwargs`, use `Unpack[TypedDict]` with the keys the code accepts (see `_BlobKwargs`). Where
  the real type lives in an untyped library (`requests.Session` for `Client(_http=...)`), use `object` and say what
  it is in a comment.
- **Private aliases stay per module.** `_Timeout`, `_Retry` and `_ETag` are redefined in each module that uses them:
  importing a `_name` from another module is `reportPrivateUsage` in pyright, and a public alias would be reported
  by stubtest as missing at runtime.
- **Stub-only public names** (e.g. `BlobIterator`, the type `list_blobs` returns) need an entry in
  `tests/allowlist.txt` and a comment in the stub saying they don't exist at runtime.
- **Return types:** properties backed by the resource's JSON (`size`, `content_type`, ...) are `X | None`, as they
  are `None` until the resource is loaded.
- **Test only what the stubs don't spell out.** stubtest already checks the signatures, so `tests/check_storage.py`
  doesn't restate annotations (no `assert_type(blob.size, int | None)`). Add a check for:
  - how imports resolve: the empty `cloud/__init__.pyi`, the `partial` fallback to unstubbed modules
  - `**kwargs: Unpack[...]`, overloads and generics, where the caller's type isn't written out in the stub
  - stub-only names, used the way the README tells callers to (`TYPE_CHECKING` import, annotations)
  - a few realistic calls, to show that the parameter types accept real values (`timeout=(3, 10)`,
    `retry=DEFAULT_RETRY`)

  Expect an error with a rule-specific ignore (`# pyright: ignore[reportCallIssue]`): `reportUnnecessaryTypeIgnoreComment`
  is an error, so the check fails if the stubs stop rejecting that call.
- When adding a class or method, also update the coverage table in `README.md`.

## Versions

The package has its own semantic version (`0.1.0`), independent of `google-cloud-storage`'s; it is not updated
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
It runs the same checks as above, builds with `uv build --no-sources`, uploads the files and rebuilds the project
and root index pages in the R2 bucket, then creates a GitHub Release from the changelog section and posts the result
to Slack. It refuses to overwrite a published version, so a bad release is fixed by publishing a new version.

The `publish` job runs in the `agnos-packages` environment, which only `v*` tags may deploy to. The R2 secrets
(`R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ACCOUNT_ID`, `R2_BUCKET`) are set on that environment;
`SLACK_WEBHOOK_URL` is an organization secret.

`scripts/build_index.py` writes the index pages with the standard library only, so it runs on the runner's system
Python. Keep it in sync with the copy in `keycloak-auth`: both rewrite the shared root index.
