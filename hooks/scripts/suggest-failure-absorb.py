#!/usr/bin/env python3
"""PostToolUse(Bash) hook: detect test failures and suggest /failure-absorb."""
import sys
import json
import re

FAILURE_PATTERNS = [
    # Common
    r'FAIL[ED]?\b',
    r'\bERROR\b',
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
    r'BUILD\s+SUCCESSFUL',
    r'passed,\s+0\s+failed',
]

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

    for pat in IGNORE_PATTERNS:
        if re.search(pat, output, re.IGNORECASE):
            sys.exit(0)

    for pat in FAILURE_PATTERNS:
        if re.search(pat, output, re.IGNORECASE):
            # Extract first matching line for context
            match_line = ""
            for line in output.splitlines():
                if re.search(pat, line, re.IGNORECASE):
                    match_line = line.strip()[:120]
                    break

            msg = {
                "systemMessage": (
                    "[Harness] Error detected. "
                    "Append this failure to docs/failure-log.md with date, error summary, and file context. "
                    "Format: `| YYYY-MM-DD | <one-line summary> | pending | - |`. "
                    "Do NOT run /failure-absorb or any verification commands automatically. "
                    f"Error: {match_line}"
                )
            }
            sys.stderr.write(json.dumps(msg))
            sys.exit(0)

    sys.exit(0)

if __name__ == "__main__":
    main()
