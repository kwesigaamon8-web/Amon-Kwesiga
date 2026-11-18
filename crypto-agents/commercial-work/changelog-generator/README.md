# Original Git Changelog Generator — B1/B2 commercial work sample

1. Install Git, Bash and Python 3.
2. Save `changelog.sh` locally or clone this repository.
3. Run `bash changelog.sh /path/to/repo /path/to/CHANGELOG.md` (omit both arguments to use the current working directory).

The script generates **Added**, **Fixed**, **Changed** and **Removed** sections from commit subjects since the latest reachable tag. It ignores merge commits, supports common Conventional Commit prefixes, and writes only the requested Markdown file. No network calls, pushes, signing or wallet access.

## Local reproducible smoke test performed 18 Nov 2026
- Initialized a temporary Git repository.
- Committed `initial` and tagged it `v0.1`.
- Committed `feat: add export` and `fix: correct parsing`.
- Ran `bash changelog.sh . ./CHANGELOG.md`.
- Verified `Added` includes `add export`, `Fixed` includes `correct parsing`, and the tagged `initial` commit is excluded.
- Test result: **PASS** on Bash/Git/Python 3 in local test container.

Example:
```markdown
# Changelog

Changes since `v0.1`.

## Added
- add export (`<commit>`)

## Fixed
- correct parsing (`<commit>`)

## Changed
- None

## Removed
- None
```

## Payment and source eligibility
Potential matching external issue: [claude-builders-bounty/claude-builders-bounty#1](https://github.com/claude-builders-bounty/claude-builders-bounty/issues/1), advertising US$50 and an Opire claim/merge process. **Not claimed, not submitted and not accepted.** The issue has thousands of comments, and Opire eligibility, available funded reward, payout network and external write permissions have not been established. This sample is therefore not an earned receivable or verified BTC payment. No third-party posting was made. A sponsor may commission a customized version via [B1/B2 paid-work request](https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/18).
