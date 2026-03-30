#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(script: str, payload: dict) -> tuple[int, str, str]:
    p = subprocess.run(
        [sys.executable, str(ROOT / script)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def assert_case(name: str, script: str, payload: dict, expected_code: int, stderr_contains=None):
    code, out, err = run(script, payload)
    ok = code == expected_code
    if not ok:
        print(f'[FAIL] {name}: expected exit {expected_code}, got {code}')
        print(f'  stdout={out!r}')
        print(f'  stderr={err!r}')
        return False
    if stderr_contains and not any(token in err for token in stderr_contains):
        print(f'[FAIL] {name}: expected stderr to contain one of {stderr_contains!r}, got {err!r}')
        return False
    print(f'[PASS] {name}')
    return True


def main():
    ok = True

    # block-destructive.py
    ok &= assert_case(
        "block-destructive-detect-rm",
        'block-destructive.py',
        {"tool_input": {"command": "rm -rf /"}},
        2,
        ["Destructive command blocked"],
    )
    ok &= assert_case(
        "block-destructive-allow-safe",
        'block-destructive.py',
        {"tool_input": {"command": "ls -la"}},
        0,
    )
    ok &= assert_case(
        "block-destructive-allow-clean-dryrun",
        'block-destructive.py',
        {"tool_input": {"command": "git clean -n"}},
        0,
    )
    ok &= assert_case(
        "block-destructive-detect-clean",
        'block-destructive.py',
        {"tool_input": {"command": "git clean -fdx"}},
        2,
        ["Destructive command blocked"],
    )

    # completion-gate.py
    ok &= assert_case(
        "completion-gate-code-block-no-lint",
        'completion-gate.py',
        {"tool_input": {"file_path": "src/main.py", "command": "pytest -q", "completion_requested": True}},
        2,
        ["BLOCK completion"],
    )
    ok &= assert_case(
        "completion-gate-code-pass",
        'completion-gate.py',
        {"tool_input": {"file_path": "src/main.py", "command": "pytest -q && ruff check src/" , "completion_requested": True}},
        0,
    )
    ok &= assert_case(
        "completion-gate-docs-pass",
        'completion-gate.py',
        {"tool_input": {"file_path": "README.md", "command": "echo docs update"}},
        0,
    )
    ok &= assert_case(
        "completion-gate-docs-completion-note",
        'completion-gate.py',
        {"tool_input": {"file_path": "README.md", "command": "echo docs update", "completion_requested": True, "summary": "completed docs edit"}},
        0,
    )
    ok &= assert_case(
        "completion-gate-read-only",
        'completion-gate.py',
        {"tool_input": {"tool_name": "Read", "completion_requested": True}},
        0,
    )
    ok &= assert_case(
        "completion-gate-config-only-no-block",
        'completion-gate.py',
        {"tool_input": {"file_path": "config/schema.json", "command": "echo changed schema" , "completion_requested": True}},
        0,
    )

    # check-docs-change.py
    ok &= assert_case(
        "check-docs-change-api-file",
        'check-docs-change.py',
        {"tool_input": {"file_path": "api/openapi.yaml"}},
        0,
        ["API/contract-related file change detected"],
    )

    # ensure non-contract file change returns no warning
    ok &= assert_case(
        "check-docs-change-no-warning",
        'check-docs-change.py',
        {"tool_input": {"file_path": "src/main.py"}},
        0,
        None,
    )

    if ok:
        print('[PASS] all harness hook selftests succeeded')
        return 0
    print('[FAIL] harness hook selftests had failures')
    return 2


if __name__ == '__main__':
    sys.exit(main())
