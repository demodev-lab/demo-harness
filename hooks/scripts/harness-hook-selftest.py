#!/usr/bin/env python3

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run(script: str, payload: dict, env=None) -> tuple[int, str, str]:
    if script.endswith('.sh'):
        cmd = ['/bin/bash', str(ROOT / script)]
    else:
        cmd = [sys.executable, str(ROOT / script)]

    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    p = subprocess.run(
        cmd,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
        env=merged_env,
    )
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def run_shell_fallback_no_python(script: str, payload: dict) -> tuple[int, str, str]:
    # Execute with a reduced PATH containing only shell helpers, no python3.
    temp_dir = tempfile.mkdtemp(prefix='harness-shell-fallback-')
    try:
        for cmd in ("cat", "sed", "grep", "tr", "head", "bash"):
            src = shutil.which(cmd)
            if src:
                os.symlink(src, os.path.join(temp_dir, cmd))
        env = os.environ.copy()
        env['PATH'] = temp_dir
        return run(script, payload, env=env)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

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


def assert_case_with_runner(name: str, script: str, payload: dict, expected_code: int, stderr_contains=None, runner=run):
    code, out, err = runner(script, payload)
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

    project_root = ROOT.parent.parent
    bad_debug_file = project_root / '.tmp_completion_gate_debug_artifacts.py'
    clean_file = project_root / '.tmp_completion_gate_clean.py'
    bad_debug_file.write_text("# TODO: remove this before merge\nprint('debug')\n", encoding='utf-8')
    clean_file.write_text("def add(a, b):\n    return a + b\n", encoding='utf-8')

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
    ok &= assert_case(
        "block-destructive-detect-rm-option-order",
        'block-destructive.py',
        {"tool_input": {"command": "rm -fr /tmp"}},
        2,
        ["Destructive command blocked"],
    )
    ok &= assert_case(
        "block-destructive-detect-rm-spaced",
        'block-destructive.py',
        {"tool_input": {"command": "rm -f -r /"}},
        2,
        ["Destructive command blocked"],
    )
    ok &= assert_case(
        "block-destructive-detect-rm-single-quoted",
        'block-destructive.py',
        {"tool_input": {"command": "rm -f -r '/'"}},
        2,
        ["Destructive command blocked"],
    )
    ok &= assert_case_with_runner(
        "block-destructive-fallback-detect-rm",
        'block-destructive.sh',
        {"tool_input": {"command": "rm -f -r /"}},
        2,
        ["Destructive command blocked"],
        runner=run_shell_fallback_no_python,
    )
    ok &= assert_case_with_runner(
        "block-destructive-fallback-detect-rm-single-quoted",
        'block-destructive.sh',
        {"tool_input": {"command": "rm -f -r '/'"}},
        2,
        ["Destructive command blocked"],
        runner=run_shell_fallback_no_python,
    )
    ok &= assert_case_with_runner(
        "block-destructive-fallback-allow-safe",
        'block-destructive.sh',
        {"tool_input": {"command": "ls -la"}},
        0,
        None,
        runner=run_shell_fallback_no_python,
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
        "completion-gate-docs-pass-legacy-wrapper",
        'completion-gate.py',
        {"tool_input": "{\"file_path\": \"README.md\", \"command\": \"echo docs update\", \"completion_requested\": true}"},
        0,
    )
    ok &= assert_case(
        "completion-gate-docs-completion-note-missing",
        'completion-gate.py',
        {
            "tool_input": {
                "file_path": "README.md",
                "command": "echo docs update",
                "completion_requested": True,
                "summary": "completed docs edit",
            }
        },
        0,
        ["Docs-only completion request detected"],
    )
    ok &= assert_case(
        "completion-gate-docs-completion-note-ok",
        'completion-gate.py',
        {
            "tool_input": {
                "file_path": "README.md",
                "command": "echo docs update",
                "completion_requested": True,
                "summary": "Docs reviewed and updated per checklist",
            }
        },
        0,
        None,
    )
    ok &= assert_case(
        "completion-gate-config-contract-notification",
        'completion-gate.py',
        {
            "tool_input": {
                "file_path": "api/openapi.yaml",
                "command": "echo docs update",
                "completion_requested": True,
            }
        },
        0,
        ["CONFIG/SCHEMA-related paths changed"],
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
    ok &= assert_case(
        "completion-gate-code-block-debug-artifacts",
        'completion-gate.py',
        {
            "tool_input": {
                "file_path": str(bad_debug_file),
                "changed_files": [str(bad_debug_file)],
                "command": "pytest -q && npm run lint",
                "completion_requested": True,
            }
        },
        2,
        ["debug_artifacts"],
    )
    ok &= assert_case(
        "completion-gate-code-pass-debug-free",
        'completion-gate.py',
        {
            "tool_input": {
                "file_path": str(clean_file),
                "changed_files": [str(clean_file)],
                "command": "pytest -q && npm run lint",
                "completion_requested": True,
            }
        },
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
    ok &= assert_case(
        "check-docs-change-api-file-legacy-wrapper",
        'check-docs-change.py',
        {"tool_input": "{\"file_path\": \"api/openapi.yaml\"}"},
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

    # suggest-failure-absorb.py
    ok &= assert_case(
        "suggest-failure-absorb-detects-failure",
        'suggest-failure-absorb.py',
        {"tool_result": "FAILED test_login - AssertionError: expected True"},
        0,
        ["failure-absorb", "Harness"],
    )
    ok &= assert_case(
        "suggest-failure-absorb-ignores-passing",
        'suggest-failure-absorb.py',
        {"tool_result": "5 passed, 0 failed in 0.15s"},
        0,
        None,
    )

    # suggest-rule-promote.py
    ok &= assert_case(
        "suggest-rule-promote-first-occurrence-silent",
        'suggest-rule-promote.py',
        {"tool_result": "Error: something went wrong in the module"},
        0,
        None,
    )
    ok &= assert_case(
        "suggest-rule-promote-empty-output-silent",
        'suggest-rule-promote.py',
        {"tool_result": ""},
        0,
        None,
    )

    # suggest-harness-audit.py
    ok &= assert_case(
        "suggest-harness-audit-with-file-path",
        'suggest-harness-audit.py',
        {"tool_input": {"file_path": "src/main.py"}},
        0,
        None,
    )
    ok &= assert_case(
        "suggest-harness-audit-no-file-path-silent",
        'suggest-harness-audit.py',
        {"tool_input": {}},
        0,
        None,
    )

    # session-doc-cleanup.py
    ok &= assert_case(
        "session-doc-cleanup-empty-stdin-graceful",
        'session-doc-cleanup.py',
        {},
        0,
        None,
    )

    if ok:
        print('[PASS] all harness hook selftests succeeded')
        bad_debug_file.unlink(missing_ok=True)
        clean_file.unlink(missing_ok=True)
        return 0
    print('[FAIL] harness hook selftests had failures')
    bad_debug_file.unlink(missing_ok=True)
    clean_file.unlink(missing_ok=True)
    return 2


if __name__ == '__main__':
    sys.exit(main())
