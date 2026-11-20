# Licensed free software reused for B1/B2 coordination

## 1. Liteq — Apache License 2.0 (source file actually copied)

- **Original repository:** https://github.com/unkloud/liteq
- **Exact pinned upstream commit:** https://github.com/unkloud/liteq/commit/6e7a6ec8c5016343b85c34ad310f3837c77cf57a
- **Upstream file:** `liteq.py`
- **Local vendored file:** `crypto-agents/vendor/liteq.py`
- **Copyright / licence:** Apache-2.0. Upstream file also embeds PSF-originated UUID source, with the upstream Python Software Foundation license included.
- **Both licence files preserved:** `LICENSE.liteq-Apache-2.0` and `LICENSE.liteq-PSF`
- **Our modification:** Replace private CPython `uuid.UUID._from_int(int_uuid_7)` with the supported public `uuid.UUID(int=int_uuid_7)` to improve compatibility with the repository's Python 3.11 GitHub Action jobs. Other source retained.
- **Purpose:** A local, persistent SQLite queue providing task claim, acknowledgement, finite retries, visibility timeout and dead-letter storage. No cloud account required for the local test.

## 2. python-jsonschema — MIT (installed as free dependency)

- **Original repository:** https://github.com/python-jsonschema/jsonschema
- **License:** MIT, https://github.com/python-jsonschema/jsonschema/blob/main/COPYING
- **Used in:** `crypto-agents/opensource_queue_worker.py` through the public installed `Draft202012Validator` API.
- **Purpose:** Reject stale, forged or malformed owner commands, mismatched parents and unauthorized task types, before executing a worker assignment.
- **Source inclusion:** The third-party package is installed from PyPI in the test environment, NOT copied into this repository; the adapter/command schema is new code.

## 3. Tenacity — Apache License 2.0 (installed as free dependency)

- **Original repository:** https://github.com/jd/tenacity
- **License:** Apache-2.0, https://github.com/jd/tenacity/blob/main/LICENSE
- **Used in:** `crypto-agents/opensource_queue_worker.py`, with finite retry on SQLite transient operational errors only.
- **Source inclusion:** Installed from PyPI into the CI environment, not copied into the repository.

## Security and deployment limitations

All code remains subject to the owner's standing restrictions: **do not access, read, search, draft or send Gmail or any emails without separate specific authorization**; no unsolicited mass marketing, wallet spending/signing, cryptocurrency mining on unauthorized devices, or fabricated customer/buyer/payment receipts.

**This is free software, not free infinite compute.** A GitHub Actions runner and its SQLite file stop when the job ends; they are NOT a persistent globally available queue or 11.25 trillion active AI agents. Scaling to authenticated independent workers across many machines requires real infrastructure, authorization, and supervision.

**No other third-party code is asserted to be vendored.** The command schema, receipts and tests are original B1/B2 integration work that uses these sources.
