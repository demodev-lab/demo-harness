#!/usr/bin/env python3
"""Stop hook: scan failure-log.md for repeated patterns, update promotion queue, flush state."""
import os
import re
import sys
from collections import Counter
from datetime import datetime

try:
    from lib.config_loader import load_config, get_project_root
except ImportError:
    def load_config(_):
        return {"agents_md_max_lines": 60}
    def get_project_root():
        cwd = os.getcwd()
        d = cwd
        while d != os.path.dirname(d):
            if os.path.isdir(os.path.join(d, '.git')):
                return d
            d = os.path.dirname(d)
        return cwd

try:
    from lib.state_manager import flush_state, add_promotion_candidate, load_state, save_state
except ImportError:
    def flush_state(_):
        return {}
    def add_promotion_candidate(s, _p, _c, _h):
        return s
    def load_state(_):
        return {}
    def save_state(_, __):
        return False


def _read_failure_log(path):
    """Parse failure-log.md — dual parser for table rows AND structured entries."""
    if not os.path.isfile(path):
        return []

    entries = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except OSError:
        return []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Parse 5-column (or 4-column) table rows
        if line.startswith('|'):
            cols = [c.strip() for c in line.split('|')[1:-1]]
            if len(cols) >= 2:
                # Skip header and separator rows
                if cols[0].lower() not in ('date', '날짜', '---', '') and not all(
                    c.startswith('-') for c in cols
                ):
                    entries.append({
                        'line_num': i,
                        'date': cols[0],
                        'summary': cols[1] if len(cols) > 1 else '',
                        'category': cols[2] if len(cols) > 2 else '',
                        'action': cols[3] if len(cols) > 3 else '',
                        'verification': cols[4] if len(cols) > 4 else '',
                        'raw': line,
                    })
            i += 1
            continue

        # Parse legacy structured entries (### [date] [title])
        if line.startswith('### '):
            entry = {'line_num': i, 'date': '', 'summary': line[4:], 'category': '',
                     'action': '', 'verification': '', 'raw': line}
            # Try to extract date from title
            date_match = re.match(r'###\s+(\d{4}-\d{2}-\d{2})\s+(.*)', line)
            if date_match:
                entry['date'] = date_match.group(1)
                entry['summary'] = date_match.group(2)
            # Read bullet list following the header
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith('- '):
                bullet = lines[j].strip()[2:]
                if bullet.lower().startswith('category:'):
                    entry['category'] = bullet.split(':', 1)[1].strip()
                elif bullet.lower().startswith('resolution:') or bullet.lower().startswith('action:'):
                    entry['action'] = bullet.split(':', 1)[1].strip()
                j += 1
            entries.append(entry)
            i = j
            continue

        i += 1

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
    pending = [e for e in entries if e.get('status', '').lower() in ('pending', '-', '')]
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

    root = get_project_root()
    config = load_config(root)
    log_path = os.path.join(root, config.get('failure_log_path', 'docs/failure-log.md'))

    # Flush session buffer to persistent state (critical: must happen at Stop)
    state = flush_state(root)

    # Skip if no failure-log exists (harness not initialized)
    if not os.path.isfile(log_path):
        return 0

    entries = _read_failure_log(log_path)
    repeated = _find_repeated_patterns(entries)
    agents_lines = _check_agents_md(root)

    warnings = []

    # Update promotion candidates in state (not directly in failure-log)
    if repeated:
        for r in repeated:
            state = add_promotion_candidate(
                state, r['pattern'], r['count'], 'command'
            )
            warnings.append(f"repeated {r['count']}x: {r['pattern'][:60]}")
        # Also mark in failure-log for visibility
        _mark_promotion_candidates(log_path, repeated)
        save_state(root, state)

    # Check AGENTS.md size
    max_lines = config.get('agents_md_max_lines', 60)
    if agents_lines and agents_lines > max_lines:
        warnings.append(
            f"AGENTS.md is {agents_lines} lines (limit: {max_lines}). "
            "Consider pruning or moving rules to skills."
        )

    if warnings:
        print("[Harness Cleanup] " + "; ".join(warnings), file=sys.stderr)

    return 0


if __name__ == '__main__':
    sys.exit(main())
