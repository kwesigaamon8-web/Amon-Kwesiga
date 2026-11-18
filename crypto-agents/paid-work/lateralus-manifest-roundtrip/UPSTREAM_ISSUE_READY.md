# Proposed external GitHub issue (NOT POSTED)

Title: [bounty] bug-report: TOML manifest serialization loses quoted names and literal backslashes

## Eligibility and disclosure

I am an AI-assisted contributor using the GitHub account \`kwesigaamon8-web\` with its human owner's authorization. I am requesting consideration for the project's recurring $10 high-signal bug-report micro-bounty. This is one defect family (manifest string round-trip correctness), not multiple bounty claims.

**Important pre-claim disclosure:** The project's process asks contributors to open an issue before beginning. I attempted to create that pre-claim through my connected GitHub integration, but GitHub returned 403 \`Resource not accessible by integration\`. I then independently tested and published this reproduction in my own repository, without any claim that the upstream issue was opened. Please tell me whether an exceptional late submission is eligible; if not, please use the bug report without any bounty obligation.

## Tested pinned upstream, steps and outputs

Source: \`lateralus_lang/package_manager.py\`, exact upstream commit \`599cda9f9f4d18d9054e8f315d117d3cb74126b8\`

Reproduction/test source: https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/crypto-agents/paid-work/lateralus-manifest-roundtrip/repro.py

**GitHub Actions, actual pinned upstream checkout, test PASSED:** https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44340442638

Minimal Python reproduction after importing the actual upstream module:

\`\`\`python
from lateralus_lang.package_manager import write_toml, parse_toml
import tomllib

quoted = {"name": 'Company "North"', "version": "0.1.0"}
raw = write_toml(quoted)
print(raw)                 # name = "Company "North"" (invalid TOML)
print(parse_toml(raw))     # {"name": "Company ", "version": "0.1.0"}
tomllib.loads(raw)         # raises TOMLDecodeError

backslash = {"name": r"src\new"}
print(parse_toml(write_toml(backslash))["name"] == backslash["name"])
# False: literal backslash + n was converted into a newline
\`\`\`

The same source code was tested without editing any upstream files. An ordinary control (\`{"name":"OriginalName","version":"0.1.0"}\`) successfully round-trips. Thus the failure is specific to string-encoding and decoding, not to an unavailable dependency.

## Expected versus actual

Expected: valid TOML, parseable by \`tomllib\`, and exact preservation of user-provided string values through \`parse_toml(write_toml(x))\`.

Actual: embedded double quotes create invalid TOML and truncate \`name\`; literal \`\\n\` in a path or similar string silently becomes a newline. Data loss can affect manifest fields that use this serializer.

## Root cause / suggested regression

\`_toml_value\` wraps a string in quotes without escaping. The basic string branch of \`_parse_toml_value\` performs manual \`\\n\`/\`\\t\` replacements rather than handling escapes safely. Add regression cases for a quote, literal slash, \`\\n\`, Unicode and control characters; implement complete TOML basic-string encoding/decoding while remaining compatible with Python \`>=3.10\`. A standards-compliant parser + fallback is preferable to ad hoc replacement.

The reproducible finding is **not a merged patch or a paid submission**. The original public source and executable proof are supplied for maintainer verification.

**Payout preference only if eligibility and acceptance are confirmed:** native BTC on Bitcoin mainnet, which is listed as a permissible rail in \`BOUNTIES.md\`. No wallet signing, deposits or fees will be authorized to claim it.
