#!/usr/bin/env python3
"""Stop hook: scan failure-log.md for repeated patterns and mark promotion candidates."""
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime


def _find_project_root():
    """Find git root or cwd."""
    cwd = os.getcwd()
    d = cwd
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, '.git')):
            return d
        d = os.path.dirname(d)
    return cwd


def _read_failure_log(path):
    """Parse failure-log.md table rows. Returns list of dicts."""
    if not os.path.isfile(path):
        return []

    entries = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except OSError:
        return []

    for i, line in enumerate(lines):
        line = line.strip()
        if not line.startswith('|'):
            continue
        cols = [c.strip() for c in line.split('|')[1:-1]]
        if len(cols) < 2:
            continue
        # Skip header and separator rows
        if cols[0].lower() in ('date', '날짜', '---', ''):
            continue
        if all(c.startswith('-') for c in cols):
            continue

        entries.append({
            'line_num': i,
            'date': cols[0],
            'summary': cols[1] if len(cols) > 1 else '',
            'status': cols[2] if len(cols) > 2 else '',
            'action': cols[3] if len(cols) > 3 else '',
            'raw': line,
        })

    return entries


def _normalize_summary(summary):
    """Normalize error summary for dedup comparison."""
    s = summary.lower().strip()
    # Remove dates, line numbers, file paths specifics
    s = re.sub(r'\d{4}-\d{2}-\d{2}', '', s)
    s = re.sub(r':\d+', '', s)
    s = re.sub(r'line\s+\d+', '', s)
    # Remove extra whitespace
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def _find_repeated_patterns(entries):
    """Find error summaries that appear 2+ times with status 'pending'."""
    pending = [e for e in entries if e['status'].lower() in ('pending', '-', '')]
    if not pending:
        return []

    normalized = [(e, _normalize_summary(e['summary'])) for e in pending]
    counter = Counter(norm for _, norm in normalized)

    repeated = []
    seen = set()
    for norm_key, count in counter.items():
        if count >= 2 and norm_key not in seen:
            seen.add(norm_key)
            matching = [e for e, n in normalized if n == norm_key]
            repeated.append({
                'pattern': norm_key,
                'count': count,
                'entries': matching,
            })

    return repeated


def _check_agents_md(root):
    """Check AGENTS.md line count."""
    agents_path = os.path.join(root, 'AGENTS.md')
    if not os.path.isfile(agents_path):
        return None

    try:
        with open(agents_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return len(lines)
    except OSError:
        return None


def _mark_promotion_candidates(log_path, repeated):
    """Append promotion candidate notes to failure-log.md."""
    if not repeated:
        return False

    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except OSError:
        return False

    # Check if promotion section already exists for today
    today = datetime.now().strftime('%Y-%m-%d')
    if f'<!-- promotion-check: {today} -->' in content:
        return False

    promotion_notes = [f'\n<!-- promotion-check: {today} -->']
    promotion_notes.append(f'\n### Promotion Candidates ({today})\n')
    promotion_notes.append('| Pattern | Count | Action |')
    promotion_notes.append('|---------|-------|--------|')

    for r in repeated:
        pattern_short = r['pattern'][:80]
        promotion_notes.append(
            f"| {pattern_short} | {r['count']}x | `/rule-promote` 검토 필요 |"
        )

    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write('\n'.join(promotion_notes) + '\n')
        return True
    except OSError:
        return False


def main():
    # Consume stdin
    try:
        sys.stdin.read()
    except Exception:
        pass

    root = _find_project_root()
    log_path = os.path.join(root, 'docs', 'failure-log.md')

    # Skip if no failure-log exists (harness not initialized)
    if not os.path.isfile(log_path):
        return 0

    entries = _read_failure_log(log_path)
    repeated = _find_repeated_patterns(entries)
    agents_lines = _check_agents_md(root)

    updated = False
    warnings = []

    # Mark promotion candidates in failure-log.md
    if repeated:
        updated = _mark_promotion_candidates(log_path, repeated)
        for r in repeated:
            warnings.append(
                f"repeated {r['count']}x: {r['pattern'][:60]}"
            )

    # Check AGENTS.md size
    if agents_lines and agents_lines > 60:
        warnings.append(
            f"AGENTS.md is {agents_lines} lines (limit: 60). "
            "Consider pruning or moving rules to skills."
        )

    if warnings:
        msg = {
            "systemMessage": (
                "[Harness Cleanup] Session-end document scan complete. "
                + "; ".join(warnings)
            ),
        }
        sys.stderr.write(json.dumps(msg))

    return 0


if __name__ == '__main__':
    sys.exit(main())
