#!/usr/bin/env python3

import json
import os
import re
from pathlib import Path
import sys


def _collect_strings(obj, max_depth=16):
    if max_depth <= 0:
        return []

    if obj is None:
        return []

    if isinstance(obj, str):
        return [obj]

    if isinstance(obj, dict):
        out = []
        for v in obj.values():
            out.extend(_collect_strings(v, max_depth - 1))
        return out

    if isinstance(obj, list):
        out = []
        for v in obj:
            out.extend(_collect_strings(v, max_depth - 1))
        return out

    return []


def _flatten_fields(payload: dict):
    fields = []
    if not isinstance(payload, dict):
        return fields

    stack = [payload]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            for k, v in cur.items():
                stack.append(v)
                if isinstance(v, (str, int, bool)):
                    fields.append((k, v))
        elif isinstance(cur, list):
            for v in cur:
                stack.append(v)
    return fields


def _collect_paths(payload):
    paths = set()
    if not isinstance(payload, dict):
        return []

    path_candidates = [
        payload.get("file_path"),
        payload.get("path"),
        payload.get("cwd"),
        payload.get("working_directory"),
        payload.get("changed_files"),
        payload.get("files"),
        payload.get("file_paths"),
        payload.get("targets"),
        payload.get("path_list"),
        payload.get("paths"),
    ]

    def _add(v):
        if isinstance(v, str):
            s = v.strip()
            if s:
                paths.add(s)
        elif isinstance(v, list):
            for x in v:
                _add(x)

    for item in path_candidates:
        _add(item)

    for s in _collect_strings(payload):
        for tok in re.findall(r"(?:^|[\s'\"\\(])([A-Za-z0-9_./-]*[/\\][A-Za-z0-9_./@-]*|\.[A-Za-z0-9_./-]+)", s):
            tok = tok.strip('\'"()')
            if tok:
                paths.add(tok)

    return sorted({p for p in paths if isinstance(p, str) and p.strip()})


def classify_files(paths):
    buckets = {"code": set(), "docs": set(), "config": set(), "other": set()}

    if not paths:
        return buckets

    code_ext = {
        '.py', '.ts', '.tsx', '.js', '.jsx', '.go', '.rb', '.rs', '.java', '.kt', '.scala', '.cs',
        '.cpp', '.c', '.h', '.hpp', '.swift', '.php', '.mjs', '.cjs', '.vue', '.svelte'
    }
    config_ext = {
        '.json', '.yaml', '.yml', '.toml', '.ini', '.env', '.cfg', '.conf', '.graphql', '.proto'
    }
    doc_ext = {'.md', '.mdx', '.txt', '.rst', '.org'}

    code_dirs = ['src/', 'lib/', 'app/', 'cmd/', 'pkg/', 'handlers/', 'controllers/', 'services/', 'routes/', 'models/', 'types/']
    doc_dirs = ['docs/', 'documentation/', 'changelog/', 'release-notes/']

    for p in paths:
        lower = p.lower().replace('\\', '/').strip()
        lower = lower.rstrip('/')
        stem = Path(lower).name
        ext = Path(lower).suffix

        if any(lower.startswith(prefix) for prefix in doc_dirs) or stem in {'readme.md', 'readme.rst', 'changelog.md'}:
            buckets['docs'].add(p)
            continue

        if ext in doc_ext:
            buckets['docs'].add(p)
        elif ext in config_ext or any(seg in lower for seg in ['.github/workflows', 'configs/', 'config/', 'schema/', 'api/', 'routes/', 'models/', 'types/']):
            buckets['config'].add(p)
        elif ext in code_ext or any(seg in lower for seg in code_dirs):
            buckets['code'].add(p)
        else:
            buckets['other'].add(p)

    return buckets


def _match_any(patterns, text):
    lowered = text.lower()
    for pat in patterns:
        m = re.search(pat, lowered)
        if m:
            return pat
    return None


def has_verification_evidence(strings, context_payload=None):
    joined = "\n".join(s.lower() for s in strings if isinstance(s, str))

    test_patterns = [
        r"\b(?:npm|pnpm|yarn|bun)\s+run\s+test\b",
        r"\b(?:npm|pnpm|yarn|bun)\s+test\b",
        r"\bpytest\b",
        r"\bgo\s+test\b",
        r"\bcargo\s+test\b",
        r"\bdotnet\s+test\b",
        r"\bphpunit\b",
        r"\bpytest\s+(-q|--maxfail|--disable-warnings)?",
        r"\bmvn\s+test\b",
        r"\bgradle\s+test\b",
        r"\bmake\s+(?:test|unit|integration)\b",
        r"\b\w*\b\s+\-m\s+pytest\b",
        r"\btox\b",
    ]

    lint_patterns = [
        r"\bruff\s+check\b",
        r"\beslint\b",
        r"\bflake8\b",
        r"\bpylint\b",
        r"\blint\b",
        r"\bgolangci-lint\b",
        r"\bgolangci\b",
        r"\bcheckstyle\b",
        r"\bshellcheck\b",
    ]

    type_patterns = [
        r"\bmypy\b",
        r"\bpyright\b",
        r"\btsc\b(?:(?:\s+--noemit|\s+--noEmit))?",
        r"\bgo\s+vet\b",
        r"\bgo\s+test\b",
    ]

    result_pass = [
        r"\b(\d+\s+passed|\d+\s+failed\s+|ok\b|all tests passed|test suite passed|\bsuccess\b|\bsucceeded\b|exit\s+code\s*:\s*0|exitcode\s*[:\s]?0)"
    ]

    result_fail = [
        r"\bfailed\b",
        r"\berror\b",
        r"\btraceback\b",
        r"\bassertionerror\b",
        r"\bnon-zero\b",
    ]

    test_match = _match_any(test_patterns, joined)
    lint_match = _match_any(lint_patterns, joined)
    type_match = _match_any(type_patterns, joined)

    pass_hit = any(re.search(p, joined) for p in result_pass)
    fail_hit = any(re.search(p, joined) for p in result_fail)

    exit_codes = []
    source_payload = context_payload if isinstance(context_payload, dict) else {}
    for k, v in _flatten_fields(source_payload):
        if isinstance(v, int) and k.lower() in {"exit_code", "exitcode", "code", "status"}:
            exit_codes.append(v)

    if exit_codes:
        if any(code and code != 0 for code in exit_codes):
            exit_status = "failed"
        elif any(code == 0 for code in exit_codes):
            exit_status = "passed"
        else:
            exit_status = "unknown"
    else:
        if pass_hit and not fail_hit:
            exit_status = "passed"
        elif fail_hit:
            exit_status = "failed"
        else:
            exit_status = "unknown"

    return {
        "has_tests": bool(test_match),
        "has_lint": bool(lint_match),
        "has_typecheck": bool(type_match),
        "evidence": {
            "test_pattern": test_match,
            "lint_pattern": lint_match,
            "typecheck_pattern": type_match,
            "result": exit_status,
        },
    }


def is_read_only_payload(payload: dict):
    if isinstance(payload.get('read_only'), bool) and payload.get('read_only'):
        return True
    if isinstance(payload.get('read_only_session'), bool) and payload.get('read_only_session'):
        return True
    if isinstance(payload.get('no_write'), bool) and payload.get('no_write'):
        return True
    if isinstance(payload.get('mode'), str) and payload.get('mode').lower() in {'read_only', 'readonly', 'explore', 'exploratory'}:
        return True

    command = payload.get('tool_name')
    if isinstance(command, str) and command.lower() in {'read', 'grep', 'glob', 'list'}:
        return True

    return False


def completion_request_explicit(payload: dict) -> bool:
    tokens = ['complete', 'completed', 'done', 'finish', 'finished', 'ready', 'ready to handoff']

    search_fields = []
    for k in ['message', 'prompt', 'summary', 'assistant_response', 'response', 'text', 'final', 'note']:
        v = payload.get(k)
        if isinstance(v, str):
            search_fields.append(v.lower())

    if payload.get('completion_requested') is True:
        return True
    if not search_fields:
        return False
    joined = ' '.join(search_fields)
    return any(tok in joined for tok in tokens)


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        data = json.loads(raw)
    except Exception:
        return 0

    payload = data.get('tool_input', {}) if isinstance(data, dict) else {}
    if not isinstance(payload, dict):
        return 0

    if is_read_only_payload(payload):
        print('{"systemMessage":"Read-only / docs-only session detected. completion-gate: INFO only."}')
        return 0

    if payload.get('skip_completion_gate') is True:
        print('{"systemMessage":"completion gate intentionally skipped by explicit flag."}')
        return 0

    changed_paths = _collect_paths(payload)
    buckets = classify_files(changed_paths)
    has_code = bool(buckets['code'])
    has_config = bool(buckets['config'])
    has_docs_only = bool(buckets['docs']) and not (has_code or has_config or buckets['other'])

    evidence = has_verification_evidence(_collect_strings(payload) + [json.dumps(payload)], context_payload=payload)
    is_complete = completion_request_explicit(payload)
    is_docs_only = not (buckets['code'] or buckets['config'] or buckets['other']) and bool(buckets['docs'])

    if has_code:
        # require quality evidence for code/config changes
        has_quality = evidence['has_tests'] and (evidence['has_lint'] or evidence['has_typecheck'])
        quality_passed = evidence['evidence']['result'] in {'passed', 'unknown'} if has_quality else False

        if not has_quality or not quality_passed:
            missing = []
            if not evidence['has_tests']:
                missing.append('tests')
            if not (evidence['has_lint'] or evidence['has_typecheck']):
                missing.append('lint_or_typecheck')
            if evidence['evidence']['result'] == 'failed':
                missing.append('verification_result indicates failure')

            out = {
                "systemMessage": (
                    "BLOCK completion: completion evidence missing or failed for code/config changes. "
                    "Required: at least one test command and one lint/typecheck evidence command. "
                    f"Missing: {', '.join(missing) or 'unknown evidence quality'}."
                ),
                "requiredEvidence": {
                    "tests": True,
                    "lintOrTypecheck": True,
                    "docAndContractCheck": True,
                },
                "evidence": {
                    "tests": evidence['has_tests'],
                    "lint": evidence['has_lint'],
                    "typecheck": evidence['has_typecheck'],
                    "result": evidence['evidence']['result'],
                    "matched": evidence['evidence'],
                },
            }
            print(json.dumps(out), file=sys.stderr)
            return 2

        return 0

    if has_docs_only:
        if is_complete and not evidence['has_tests'] and not evidence['has_lint'] and not evidence['has_typecheck']:
            out = {
                "systemMessage": (
                    "Docs-only completion request detected. No verification commands found in payload; "
                    "approve if explicit docs review note is present, otherwise add short verification note."
                )
            }
            print(json.dumps(out), file=sys.stderr)
        return 0

    if has_config and not is_docs_only:
        out = {
            "systemMessage": (
                "CONFIG/SCHEMA-related paths changed. Capture a contract/check command output in session context "
                "(e.g., docs update check, schema validation, API lint)."
            )
        }
        print(json.dumps(out), file=sys.stderr)

    return 0


if __name__ == '__main__':
    sys.exit(main())
