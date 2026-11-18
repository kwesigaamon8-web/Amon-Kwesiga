# Release ZIP payload comparison

An original, offline work sample that compares the regular-file contents of two local ZIP archives. It reports added, removed and changed paths, SHA-256 hashes and byte counts. Archive byte equality, member metadata, member order and empty-directory differences are separate fields.

**Uncommissioned prototype:** no buyer has accepted this work and no payment has been earned. Comparing two supplied ZIP files does not rebuild source, verify reproducible builds, authenticate a publisher, validate signatures or establish that software is trustworthy.

## Run

Python 3.9 or later; standard library only. No package installation, extraction, executable launch, network access or wallet operation is used.

```sh
python zip_payload_diff.py release-a.zip release-b.zip > comparison.json
python -m unittest -v
```

A successful comparison exits `0`, including when payloads differ. Invalid, unsupported, unreadable or over-limit input exits `2` with a JSON error on stderr. Expected archive failures do not print a traceback. Successful comparison reports omit the input archive filenames. Operating-system errors can include an input path; review error text before sharing it.

The report is deterministic for unchanged inputs and limits; it includes no observation time. Path lists are sorted. `archive_bytes_equal` requires matching lengths and SHA-256 values followed by a bounded direct byte comparison. `payloads_equal` compares regular-file paths, decompressed byte counts and SHA-256 hashes; directory entries are tracked separately. Empty-directory or permission changes can matter operationally even when payloads match.

## Limits and rejected inputs

Default limits per archive: 64 MiB archive bytes, 2,000 members including directories, 32 MiB uncompressed bytes per member and 128 MiB total uncompressed bytes. The central directory is counted before `zipfile` allocates its member objects; changing only its advertised count cannot evade the member limit. Compressed content is read in chunks and CRC errors fail the comparison.

Overrides are available as `--max-archive-bytes`, `--max-members`, `--max-member-bytes` and `--max-total-bytes`; all must be positive integers. Raising limits weakens the resource bound.

The tool rejects duplicate member paths, file/directory name aliases, absolute and drive-qualified names, backslashes, empty/dot/parent path components, symlinks, special-file entries and encrypted members. It accepts only ordinary single-volume, non-ZIP64 archives using stored or deflated compression. Nonstandard central-directory layouts are rejected. No member is extracted or executed.

## Interpretation and limits

- A metadata difference is an observed difference, not a diagnosis of its cause. The selected metadata fields are not an exhaustive ZIP-forensics inventory.
- Matching payloads do not prove matching source, compiler, dependencies or build environment. An actual reproducibility claim needs a separately authorized rebuild and documented provenance.
- SHA-256 compares file content; this tool does not inspect whether content is malicious, licensed or useful.
- Paths are case-sensitive and are not normalized for Unicode or target operating systems. This is not an extraction-compatibility guarantee.
- Keep inputs stable during inspection. A size/mtime check detects ordinary concurrent changes, but this is not protection against a malicious process modifying local files and restoring their metadata.
- This is a limited offline prototype, not a general sandbox for arbitrary untrusted formats. Even with these size/count bounds, use normal OS resource isolation for hostile inputs.

The synthetic test suite exercises identical payloads with differing metadata/compression, content changes, additions/removals, deterministic output, directory handling, duplicate and unsafe paths, symlinks, all four limits, a forged central-directory count, corrupt CRCs and readable CLI failure.

## Real problem, buyer market and proposed pilot

[The SatoshiPortal/Bull Bitcoin build-validation request](https://github.com/SatoshiPortal/bdk-flutter/issues/1) documents a real release-verification problem. However, the maintainer [closed that bounty to new entries on 13 June 2026](https://github.com/SatoshiPortal/bdk-flutter/issues/1#issuecomment-4697816971). This sample is **not a submission, claimed fix, replacement for its build work, or entitlement to its advertised reward**. It uses only synthetic archive contents.

Named prospective market: Bitcoin library and wallet-release maintainers, such as the BDK language-binding ecosystem. No maintainer has commissioned this sample. The possible service is a narrow release-payload drift report for one buyer-authorized pair of ZIP files, with explanations of changed content and packaging metadata.

Proposed, unagreed pilot fee: **15,000 sats in native BTC mainnet**. A real buyer would need to confirm the input scope, deadline, acceptance criteria and direct-mainnet payment before material commissioned work. There is no awarded job, invoice, fee agreement or payment. A separately approved receiving arrangement would be required for any other network.

Acceptance proposal: demonstrate the report on a known same-payload/different-metadata pair and a deliberately changed payload, then apply it to the agreed archives within the documented bounds. The report must retain unknowns and must not label matching payloads as a reproducible-build proof.

## Existing alternatives

[diffoscope](https://diffoscope.org/) is the stronger existing choice for deep, multi-format and recursive binary investigation. A whole-archive SHA-256 comparison cheaply detects exact archive differences but does not explain which members differ. Python's [zipfile documentation](https://docs.python.org/3/library/zipfile.html) describes the underlying archive interface and format limits.

This prototype deliberately has a smaller scope: standard-library-only ZIP payload inventory, predictable JSON, explicit resource limits and no extraction or executable launch. It does not claim to invent archive comparison or replace diffoscope. The saleable part would be a buyer-specific interpretation and accepted deliverable, which remain unvalidated.

## Recorded validation

On 18 November 2026, the implementation worker and coordinator each ran the synthetic suite successfully: **15 tests passed**. The coordinator separately generated [example.json](example.json): equal file payloads, unequal archive bytes, and an observed timestamp/comment difference. No third-party release, wallet, source build or production platform was exercised.
