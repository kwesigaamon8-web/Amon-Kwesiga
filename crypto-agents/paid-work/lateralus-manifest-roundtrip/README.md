# Reproducible Lateralus TOML manifest data loss — 18 November 2026

**Classification: independently reproduced original bug finding; NOT submitted upstream; NOT claimed; NOT accepted; NOT payable; NOT paid.**

Upstream: https://github.com/bad-antics/lateralus-lang
Pinned exact upstream code: https://github.com/bad-antics/lateralus-lang/blob/599cda9f9f4d18d9054e8f315d117d3cb74126b8/lateralus_lang/package_manager.py
Original verified run: https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44340442638

## Defect and user impact

The manifest serializer's string case, \`_toml_value(v)\`, returns a double-quoted value without escaping embedded quotes or literal backslashes. In the same module the hand-written TOML parser's basic-string branch strips outer quotes and performs ad hoc replacements. Thus project name, description, author, main path or other string metadata can be rejected by standards-compliant TOML parsers **or silently changed by the project's own parser** after serialization. This is particularly relevant for paths with literal \`\\n\` sequences.

### Reproduction on actual unmodified upstream

Use \`repro.py\` in this folder against \`lateralus_lang/package_manager.py\` from the pinned upstream commit, with Python 3.11.

1. Ordinary control \`{"name":"OriginalName","version":"0.1.0"}\`: both \`tomllib\` and the project's parser reproduce the original values.
2. Quoted string \`{"name":"Company \"North\"","version":"0.1.0"}\`: serialization produces \`name = "Company "North""\`. \`tomllib.loads\` rejects it; the project's own parser returns only \`Company \` (truncated).
3. Literal backslash case \`{"name":"src\\new"}\`: serialization emits a single literal backslash followed by \`n\`. Both parsers turn that into a newline, silently changing the original value.

**Pinned CI result: two reproducible failures, one valid control.** The test deliberately succeeds only when both regressions are observed on upstream, so green CI means *defect reproduced*, not fixed.

## Proposed narrow correction and acceptance

- Escape TOML basic-string contents on output (quote, backslash and control characters); a serialization function must be a proper encoder rather than \`f'"{value}"'\`.
- Decode backslash escape sequences correctly on input (including literal \`\\\`); keep the module compatible with declared Python \`>=3.10\`. Using an established TOML parser such as Python 3.11+'s \`tomllib\` plus an appropriate Python 3.10 fallback is preferable to ad hoc string replacements for the entire manifest.
- Add round-trip and standards-parser regressions for plain strings, embedded quotes, literal backslash-n, ordinary Windows paths, unicode text and control characters. Confirm existing manifest behaviors do not regress.

## Real bounty and practical blocker

The project's [BOUNTIES.md](https://github.com/bad-antics/lateralus-lang/blob/main/BOUNTIES.md) lists a **recurring $10** bounty for an accepted high-signal bug report, says claim before beginning work, one bounty per person per quarter, and lists BTC/LN as a payment option. Its funding, available award, eligibility, acceptance and payout timing are not independently confirmed by this finding.

An actual authenticated attempt to create a pre-claim issue in the external repository returned **GitHub HTTP 403: Resource not accessible by integration**. Thus the project has not received this finding and no bounty was reserved. An eligible external GitHub issue or maintainer acceptance is necessary before any payment can be sought. No emails were read, drafted or sent, and no transactions were signed.

The project account and proof are public; personal secrets and any customer files were not accessed.
