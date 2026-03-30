#!/usr/bin/env python3
"""PostToolUse(Bash) hook: detect test failures and suggest /failure-absorb."""
import sys
import json
import re

FAILURE_PATTERNS = [
    r'FAIL[ED]?\b',
    r'\bERROR\b',
    r'AssertionError',
    r'assert\.?\w*Error',
    r'Test\s+failed',
    r'Tests?\s+\d+\s+failed',
    r'npm\s+ERR!',
    r'FAILED\s+test',
    r'pytest.*FAILED',
    r'failures?:\s*[1-9]',
    r'errors?:\s*[1-9]',
    r'Exception\b',
    r'Traceback \(most recent call last\)',
    r'exit\s+code\s+[1-9]',
    r'BUILD\s+FAIL',
    r'compilation?\s+error',
]

IGNORE_PATTERNS = [
    r'hook\s+success',
    r'Successfully',
    r'0\s+failed',
    r'0\s+errors?',
    r'All\s+tests?\s+passed',
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
            msg = {
                "systemMessage": (
                    "[Harness] Test failure or error detected. "
                    "Consider running /failure-absorb to classify this failure "
                    "and absorb it into the appropriate harness layer for prevention."
                )
            }
            sys.stderr.write(json.dumps(msg))
            sys.exit(0)

    sys.exit(0)

if __name__ == "__main__":
    main()
