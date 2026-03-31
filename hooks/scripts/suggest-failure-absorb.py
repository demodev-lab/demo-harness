#!/usr/bin/env python3
"""PostToolUse(Bash) hook: detect test failures and suggest /failure-absorb."""
import sys
import json
import re
import hashlib
import os

try:
    from lib.config_loader import load_config, get_project_root
except ImportError:
    def load_config(_):
        return {"suggestion_cooldown_seconds": 300}
    def get_project_root():
        return os.getcwd()

try:
    from lib.state_manager import (load_state, buffer_state, check_cooldown,
                                    update_suggestion_cooldown, record_failure)
except ImportError:
    def load_state(_):
        return {"suggestion_cooldowns": {}, "failures": {"total": 0, "by_category": {}}}
    def buffer_state(_):
        pass
    def check_cooldown(_s, _e, _c):
        return False
    def update_suggestion_cooldown(s, _e):
        return s
    def record_failure(s, _c, _d, _e):
        return s

# 2-tier auto-classification: 3 high-confidence patterns + Cat 0 (unclassified)
CATEGORY_HEURISTICS = {
    2: [r'ImportError', r'ModuleNotFoundError', r'Cannot\s+find\s+module',
        r'Module\s+not\s+found', r'ERR_MODULE_NOT_FOUND', r'Package.*not\s+found'],
    3: [r'AssertionError', r'assert.*failed', r'pytest.*FAILED', r'jest.*failed',
        r'vitest.*fail', r'FAIL\s+src/', r'Tests?\s+\d+\s+failed', r'test.*fail',
        r'FAIL(ED)?\s+test', r'failures?:\s*[1-9]', r'Some\s+tests\s+failed'],
    5: [r'TimeoutError', r'Timeout', r'ETIMEDOUT', r'timed?\s*out'],
}

FAILURE_PATTERNS = [
    # Common
    r'\bFAIL(ED)?\b',
    r'\bERROR\b',
    r'Test\s+failed',
    r'Tests?\s+\d+\s+failed',
    r'FAILED\s+test',
    r'failures?:\s*[1-9]',
    r'errors?:\s*[1-9]',
    r'Exception\b',
    r'exit\s+code\s+[1-9]',
    r'BUILD\s+FAIL',
    r'compilation?\s+error',
    # Python
    r'AssertionError',
    r'assert\.?\w*Error',
    r'pytest.*FAILED',
    r'Traceback \(most recent call last\)',
    # Java
    r'BUILD\s+FAILURE',
    r'mvn.*FAILURE',
    r'gradle.*FAILED',
    r'java\.\w+Exception',
    r'at\s+[\w.]+\([\w.]+:\d+\)',
    r'Tests?\s+run:.*Failures:\s*[1-9]',
    r'CompilationFailureException',
    # TypeScript additional
    r'yarn\s+ERR!',
    r'pnpm\s+ERR!',
    r'Cannot\s+find\s+module',
    r'Module\s+not\s+found',
    # Java additional
    r'ClassNotFoundException',
    r'NoSuchMethodError',
    r'Caused\s+by:',
    r'COMPILATION\s+ERROR',
    r'>\s+Task\s+:.*FAILED',
    # Dart additional
    r'Unhandled\s+Exception:',
    r'Package.*not\s+found',
    # Python additional
    r'ModuleNotFoundError',
    r'ImportError',
    # TypeScript / JavaScript
    r'npm\s+ERR!',
    r'TypeError\b',
    r'ReferenceError\b',
    r'SyntaxError\b',
    r'TS\d{4}:',
    r'error\s+TS\d+',
    r'jest.*failed',
    r'vitest.*fail',
    r'FAIL\s+src/',
    r'ERR_MODULE_NOT_FOUND',
    # Dart / Flutter
    r'flutter.*error',
    r'dart.*error',
    r'FormatException',
    r'StateError',
    r'RangeError',
    r'Unhandled\s+exception',
    r'Some\s+tests\s+failed',
    r'flutter\s+test.*fail',
    r'pub\s+get\s+failed',
    r'analysis_options.*error',
]

IGNORE_PATTERNS = [
    r'hook\s+success',
    r'Successfully',
    r'0\s+failed',
    r'0\s+errors?',
    r'All\s+tests?\s+passed',
    r'no\s+issues\s+found',
    r'No\s+errors\s+found',
    r'BUILD\s+SUCCE',
    r'passed,\s+0\s+failed',
    r'dart\s+analyze.*no\s+issues',
    r'flutter\s+test.*All\s+tests\s+passed',
]


def _extract_error_sig(match_line):
    """Create a stable signature from an error line for cooldown dedup."""
    sig = re.sub(r'\d+', 'N', match_line)
    sig = re.sub(r'/\S+/', '/PATH/', sig)
    return hashlib.md5(sig.encode()).hexdigest()[:12]


def _classify_error(match_line):
    """2-tier classification: returns category int (2, 3, 5) or 0 (unclassified)."""
    for cat, patterns in CATEGORY_HEURISTICS.items():
        for pat in patterns:
            if re.search(pat, match_line, re.IGNORECASE):
                return cat
    return 0


def _append_to_failure_log(root, config, match_line, category):
    """Auto-record failure to failure-log.md in 5-column format."""
    import time
    log_path = os.path.join(root, config.get("failure_log_path", "docs/failure-log.md"))
    if not os.path.isfile(log_path):
        return
    date_str = time.strftime("%Y-%m-%d")
    summary = match_line[:100].replace("|", "/")
    cat_label = f"Cat {category}" if category > 0 else "unclassified"
    row = f"| {date_str} | {summary} | {cat_label} | pending | unverified |"
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(row + "\n")
    except OSError:
        pass


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    output = data.get("tool_result", "") or ""
    if isinstance(output, dict):
        output = json.dumps(output)

    if not output or len(output) < 10:
        sys.exit(0)

    for pat in FAILURE_PATTERNS:
        if re.search(pat, output, re.IGNORECASE):
            match_line = ""
            for line in output.splitlines():
                if re.search(pat, line, re.IGNORECASE):
                    if any(re.search(ip, line, re.IGNORECASE) for ip in IGNORE_PATTERNS):
                        continue
                    match_line = line.strip()[:120]
                    break

            if not match_line:
                continue

            # Cooldown check — suppress duplicate suggestions within cooldown window
            root = get_project_root()
            config = load_config(root)
            state = load_state(root)
            error_sig = _extract_error_sig(match_line)

            if check_cooldown(state, error_sig, config["suggestion_cooldown_seconds"]):
                sys.exit(0)

            # Auto-classify (2-tier: Cat 2/3/5 or Cat 0)
            category = _classify_error(match_line)

            # Auto-record to failure-log.md in 5-column format
            _append_to_failure_log(root, config, match_line, category)

            # Update state: cooldown + failure record
            new_state = update_suggestion_cooldown(state, error_sig)
            new_state = record_failure(new_state, category, match_line[:120], error_sig)
            buffer_state({
                "suggestion_cooldowns": new_state.get("suggestion_cooldowns", {}),
                "failures": new_state.get("failures", {}),
            })

            cat_label = f"Cat {category}" if category > 0 else "unclassified"
            msg = {
                "systemMessage": (
                    f"[Harness] Error detected ({cat_label}). "
                    f"Error: {match_line}\n"
                    "Auto-recorded to failure-log.md. "
                    "Consider running /failure-absorb to review classification and absorb it "
                    "into the harness for permanent prevention."
                )
            }
            sys.stderr.write(json.dumps(msg))
            sys.exit(0)

    sys.exit(0)

if __name__ == "__main__":
    main()
