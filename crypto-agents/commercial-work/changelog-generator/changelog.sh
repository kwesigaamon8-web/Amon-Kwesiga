#!/usr/bin/env bash
set -euo pipefail
# Generate a deterministic changelog from commits since the latest reachable tag.
# Usage: bash changelog.sh [repository-directory] [output-file]
repo=${1:-.}
output=${2:-CHANGELOG.md}
git -C "$repo" rev-parse --is-inside-work-tree >/dev/null
last_tag=$(git -C "$repo" describe --tags --abbrev=0 2>/dev/null || true)
if [[ -n "$last_tag" ]]; then range="${last_tag}..HEAD"; else range=HEAD; fi
commits=$(git -C "$repo" log "$range" --format='%h%x09%s' --no-merges)
CHANGELOG_COMMITS="$commits" CHANGELOG_TAG="$last_tag" python3 - "$output" <<'PY'
import os,sys,re
from pathlib import Path
commits=os.environ.get('CHANGELOG_COMMITS','').splitlines()
tag=os.environ.get('CHANGELOG_TAG','')
groups={x:[] for x in ('Added','Fixed','Changed','Removed')}
for line in commits:
    if '\t' not in line: continue
    sha,msg=line.split('\t',1)
    match=re.match(r'^(feat|fix|perf|refactor|docs|style|test|build|ci|chore|revert)(?:\([^)]*\))?!?:\s*(.+)$',msg,re.I)
    if match:
        typ,desc=match.group(1).lower(),match.group(2)
        category={'feat':'Added','fix':'Fixed','revert':'Removed'}.get(typ,'Changed')
    else:
        desc=msg
        category='Removed' if re.search(r'\b(remove|delete|drop)\b',msg,re.I) else 'Changed'
    groups[category].append(f'- {desc} (`${sha}`)')
sections=['# Changelog','',f'Changes since `${tag}`.' if tag else 'Changes from repository history.','']
for category,items in groups.items():
    sections.extend([f'## {category}',*(items or ['- None']),''])
Path(sys.argv[1]).write_text('\n'.join(sections).rstrip()+'\n',encoding='utf-8')
PY
printf 'Wrote %s (%s)\n' "$output" "${last_tag:-all commits}"
