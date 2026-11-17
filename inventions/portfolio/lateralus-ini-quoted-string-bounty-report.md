# Candidate US$10 bug-bounty report: quoted INI strings lose their types

**Project:** [bad-antics/lateralus-lang](https://github.com/bad-antics/lateralus-lang)  
**Affected file:** [stdlib/ini.ltl](https://github.com/bad-antics/lateralus-lang/blob/main/stdlib/ini.ltl)  
**Published program:** [BOUNTIES.md](https://github.com/bad-antics/lateralus-lang/blob/main/BOUNTIES.md) advertises a **$10 original, high-signal bug report with minimal reproducer**, one bounty per person per quarter; payment via BTC/LN, Ko-Fi, or GitHub Sponsors, at project approval and according to their rules.  
**Status:** SOURCE-TRACED, not run in a Lateralus interpreter. NOT CLAIMED, NOT ASSIGNED, NOT AWARDED.  
**Date:** 2026-11-17

## Problem

When parsing an INI file, the module removes quotes from a scalar value **before** passing the result through `_parse_value`, which converts reserved words to booleans or null. This changes the data type of an explicitly quoted string.

## Minimal input

```ini
[demo]
quoted_true = "true"
quoted_false = "false"
quoted_null = "null"
quoted_yes = "yes"
quoted_no = "no"
quoted_nil = "nil"
ordinary = "hello"
unquoted_true = true
```

## Expected

For all values explicitly surrounded by double quotes, `get` should return the literal string value (e.g., `"false"` is a string), whereas bare `true` may be parsed as Boolean true, consistent with the module's existing coercion behavior.

## Source-code reproduction and actual predicted behavior

At [stdlib/ini.ltl](https://github.com/bad-antics/lateralus-lang/blob/main/stdlib/ini.ltl), inside `parse(text)`:

```lateralus
if len(v) >= 2 and starts_with(v, "\"") and ends_with(v, "\"") {
    v = substr(v, 1, len(v) - 2)
}
...
section[k] = _parse_value(v)
```

The same file's `_parse_value(s)` returns Boolean true for `true`/`yes`, Boolean false for `false`/`no`, and `nil` for `nil`/`null`. Thus the quoted value `"false"` is reduced to `false` and converted to a Boolean; `"null"` is reduced to `null` and converted to nil. This is a deterministic source-path conclusion, **not a claimed executed runtime result**.

| Input value | Expected type | Source-path outcome |
|---|---|---|
| `"true"` | string | Boolean true |
| `"false"` | string | Boolean false |
| `"null"` | string | nil |
| `"yes"` | string | Boolean true |
| `"no"` | string | Boolean false |
| `"nil"` | string | nil |
| `"hello"` | string | string "hello" |
| `true` | Boolean (policy dependent) | Boolean true |

## Impact

Configuration literals that need to retain the text `"false"` or `"null"` silently lose their original types. The serialization code also writes values using `str(val)` without type-sensitive escaping, so quote-preserving round-trip behavior merits its own regression tests.

## Proposed minimal fix

Track whether a field was quoted. If so, remove the quotes and store **the string directly**. Only apply `_parse_value` to unquoted fields. Add regression tests for all keyword-shaped quoted strings and both text/boolean cases.

## Authorship and evidence

This is original AI-assisted static source review performed through the GitHub account owner's authorized connection. Existing GitHub issue search for *INI parser*, *quoted boolean*, and *bencode encode* returned no duplicate matching this exact issue. A real Lateralus runtime was unavailable in the current execution environment, so the submitter must **not** claim a passing or failing runtime test. Contributors should verify with the project's actual test runner before asserting execution success.

## Submission and payout gate

The GitHub connection returned **403 Resource not accessible by integration** when attempting to [open an issue in the upstream project](https://github.com/bad-antics/lateralus-lang/issues/new); the issue was not filed. No payer has accepted work, no payable obligation has been created, and no transfer is owed. The owner can post the source-verified report through an authorized account, subject to the maintainer's policies and their decision on bounty eligibility. If approved, use the owner's already specified BTC-mainnet receiving route, not a Lightning invoice or unsupported network.
