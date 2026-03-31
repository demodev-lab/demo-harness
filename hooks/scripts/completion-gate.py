#!/usr/bin/env python3

import json
import os
import re
import subprocess
from pathlib import Path
import sys


def _normalize_path(value: str) -> str:
    if not isinstance(value, str):
        return ""
    p = value.strip().strip("\t\n\r \"'`()").strip()
    if not p:
        return ""
    # normalize Windows paths for cross-platform detection
    p = p.replace("\\", "/")
    # keep relative paths stable across runs
    if p.startswith("./"):
        p = p[2:]
    while p.startswith("./"):
        p = p[2:]
    return p


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
            s = _normalize_path(v)
            if s:
                paths.add(s)
        elif isinstance(v, list):
            for x in v:
                _add(x)

    for item in path_candidates:
        _add(item)

    for s in _collect_strings(payload):
        for tok in re.findall(r"(?:^|[\s'\"\\(])([A-Za-z0-9_./-]*[/\\][A-Za-z0-9_./@-]*|\.[A-Za-z0-9_./-]+)", s):
            normalized = _normalize_path(tok)
            if normalized:
                paths.add(normalized)

    return sorted({p for p in paths if isinstance(p, str) and p.strip()})


def _iter_file_lines(path: Path):
    try:
        with path.open('r', encoding='utf-8', errors='ignore') as fp:
            for idx, line in enumerate(fp, 1):
                yield idx, line
    except OSError:
        return


def _extract_payload(payload_or_text):
    if isinstance(payload_or_text, dict):
        return payload_or_text

    if isinstance(payload_or_text, str):
        try:
            parsed = json.loads(payload_or_text)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return {}

    return {}


def scan_debug_artifacts(paths, payload: dict):
    artifacts = []
    if not isinstance(payload, dict) or not isinstance(paths, (list, tuple, set)):
        return artifacts

    workdir = payload.get('working_directory') or payload.get('cwd') or os.getcwd()
    debug_patterns = {
        'console.log': re.compile(r"\bconsole\.log\s*\("),
        'debugger': re.compile(r"\bdebugger\b"),
        'TODO': re.compile(r"\bTODO\b"),
        'FIXME': re.compile(r"\bFIXME\b"),
        'pdb.set_trace': re.compile(r"\bpdb\.set_trace\b"),
        'breakpoint()': re.compile(r"\bbreakpoint\s*\("),
        'import pdb': re.compile(r"^\s*import\s+pdb\b|^\s*from\s+pdb\s+import\b"),
    }

    candidate_ext = {
        '.py', '.ts', '.tsx', '.js', '.jsx', '.java', '.kt', '.scala', '.rb', '.go', '.rs', '.c', '.cpp', '.h', '.hpp', '.cs', '.swift', '.php', '.vue', '.svelte'
    }

    for raw_path in paths:
        if not isinstance(raw_path, str):
            continue
        candidate = _normalize_path(raw_path)
        if not candidate:
            continue

        # avoid evaluating cwd itself or top-level directories when mistakenly picked
        if candidate in {'/', '.', '..'}:
            continue

        p = Path(candidate)
        if not p.is_absolute():
            p = Path(workdir) / p

        ext = p.suffix.lower()
        if not p.is_file() or ext not in candidate_ext:
            continue

        for lineno, line in _iter_file_lines(p):
            # Skip pattern definitions and comments to avoid false positives
            stripped = line.strip()
            if 're.compile' in stripped or stripped.startswith('#') or stripped.startswith('//'):
                continue
            for name, pattern in debug_patterns.items():
                if pattern.search(line):
                    artifacts.append({
                        'file': str(candidate),
                        'line': lineno,
                        'pattern': name,
                        'snippet': line.strip()[:140],
                    })
                    # keep one hit per file for quick signal; enough to block and avoid spam
                    break

    return artifacts


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
        r'\bflutter\s+test\b',
        r'\bdart\s+test\b',
        r'\bflutter\s+drive\b',
        r'\b\.\/gradlew\s+test\b',
        r'\b\.\/mvnw\s+test\b',
        r'\bmvn\s+verify\b',
        r'\bvitest\b',
        r'\bbun\s+test\b',
    ]

    lint_patterns = [
        r"\bruff\s+check\b",
        r"\bnpm\s+run\s+lint\b",
        r"\bpnpm\s+run\s+lint\b",
        r"\byarn\s+run\s+lint\b",
        r"\beslint\b",
        r"\bflake8\b",
        r"\bpylint\b",
        r"\blint\b",
        r"\bgolangci-lint\b",
        r"\bgolangci\b",
        r"\bcheckstyle\b",
        r"\bshellcheck\b",
        r'\bdart\s+analyze\b',
        r'\bflutter\s+analyze\b',
        r'\bbiome\s+check\b',
        r'\bbiome\s+lint\b',
        r'\bktlint\b',
        r'\bdart\s+format\b',
    ]

    type_patterns = [
        r"\bmypy\b",
        r"\bpyright\b",
        r"\btsc\b(?:(?:\s+--noemit|\s+--noEmit))?",
        r"\bgo\s+vet\b",
        r"\bdeno\s+check\b",
        r'\bflutter\s+analyze\b',
        r'\bdart\s+analyze\b',
        r'\bjavac\b',
        r'\b\.\/gradlew\s+compileJava\b',
        r'\bmvn\s+compile\b',
        r'\bvue-tsc\b',
    ]

    contract_patterns = [
        r"\bopenapi\b",
        r"\bspectral\b",
        r"\bschema\b\s+(?:validation|lint|check)\b",
        r"\bprisma\s+format\b",
        r"\bswag\b",
        r"\bopenapi-generator\b",
        r"\bprotoc\b",
    ]

    # Exit-like success / failure signatures in text output
    result_pass = [
        r"\b(\d+\s+passed|ok\b|all tests passed|test suite passed|\bsuccess\b|\bsucceeded\b|exit\s+code\s*:\s*0|exitcode\s*[:\s]?0)"
    ]

    result_fail = [
        r"\bfailed\b",
        r"\berror\b",
        r"\btraceback\b",
        r"\bassertionerror\b",
        r"\bnon-zero\b",
        r"\bcommand failed\b",
    ]

    test_match = _match_any(test_patterns, joined)
    lint_match = _match_any(lint_patterns, joined)
    type_match = _match_any(type_patterns, joined)
    contract_match = _match_any(contract_patterns, joined)

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
        "has_contract_check": bool(contract_match),
        "evidence": {
            "test_pattern": test_match,
            "lint_pattern": lint_match,
            "typecheck_pattern": type_match,
            "contract_check_pattern": contract_match,
            "result": exit_status,
        },
    }


def is_read_only_payload(payload: dict):
    if not isinstance(payload, dict):
        return True

    if isinstance(payload.get('read_only'), bool) and payload.get('read_only'):
        return True
    if isinstance(payload.get('read_only_session'), bool) and payload.get('read_only_session'):
        return True
    if isinstance(payload.get('no_write'), bool) and payload.get('no_write'):
        return True
    if isinstance(payload.get('mode'), str) and payload.get('mode').lower() in {'read_only', 'readonly', 'explore', 'exploratory'}:
        return True

    command = payload.get('tool_name')
    if isinstance(command, str) and command.lower() in {'read', 'grep', 'glob', 'list', 'search'}:
        return True

    # Non-mutating tool hints
    if payload.get('tool') in {'Read', 'ReadFile', 'Glob', 'Grep', 'List'}:
        return True

    return False


def completion_request_explicit(payload: dict) -> bool:
    tokens = [
        'complete', 'completed', '완료', 'done', 'finish', 'finished', 'ready', 'ready to handoff',
        'handoff', 'all set', 'finish work', '작업 완료', '업무 완료', 'done!', 'ready to merge',
    ]

    search_fields = []
    for k in ['message', 'prompt', 'summary', 'assistant_response', 'response', 'text', 'final', 'note', 'user_message', 'completion_note']:
        v = payload.get(k)
        if isinstance(v, str):
            search_fields.append(v.lower())

    if payload.get('completion_requested') is True:
        return True
    if payload.get('completion') is True:
        return True

    if not search_fields:
        return False
    joined = ' '.join(search_fields)
    return any(tok in joined for tok in tokens)


def has_docs_review_signal(payload: dict) -> bool:
    check_tokens = [
        'docs reviewed', 'documentation reviewed', 'docs update', 'documentation updated', '문서 리뷰',
        '문서 검토', '문서 확인', '문서 업데이트', 'readme updated', 'README updated',
    ]
    joined = ''
    for k in ['summary', 'assistant_response', 'response', 'text', 'final', 'note', 'message', 'prompt']:
        v = payload.get(k)
        if isinstance(v, str):
            joined += ' ' + v.lower()
    return any(tok in joined for tok in check_tokens)


def is_contract_path(path: str) -> bool:
    if not isinstance(path, str):
        return False

    lower_path = path.lower().strip()
    if not lower_path:
        return False

    contract_patterns = ['openapi', 'schema', 'swagger', 'api-contract', 'proto', 'graphql', 'grpc']
    if any(p in lower_path for p in contract_patterns):
        return True

    if any(lower_path.endswith(ext) for ext in ('.yaml', '.yml', '.json', '.graphql', '.proto')) and any(seg in lower_path for seg in ('api/', 'schema/', 'contracts/', 'routes/')):
        return True

    return False


def _get_git_changed_files():
    """Get actually changed files from git (staged + unstaged)."""
    files = set()
    try:
        for cmd in [
            ['git', 'diff', '--name-only'],
            ['git', 'diff', '--name-only', '--cached'],
        ]:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                files.update(f.strip() for f in result.stdout.strip().split('\n') if f.strip())
    except Exception:
        pass
    return sorted(files)


def _get_git_root():
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return os.getcwd()


def main():
    # Consume stdin (required by hook protocol) but don't rely on it for file detection
    try:
        sys.stdin.read()
    except Exception:
        pass

    # Use git to detect actual file changes — Stop hook payload lacks this info
    changed_paths = _get_git_changed_files()
    if not changed_paths:
        return 0

    buckets = classify_files(changed_paths)
    has_code = bool(buckets['code'])
    has_config = bool(buckets['config'])

    if not has_code and not has_config:
        return 0

    # Debug artifact scan — verifiable by reading actual files, so safe to BLOCK
    git_root = _get_git_root()
    debug_artifacts = scan_debug_artifacts(changed_paths, {'cwd': git_root})

    if debug_artifacts:
        out = {
            "systemMessage": (
                "BLOCK: debug artifacts found in changed files. "
                "Remove all debug statements and markers before completing. See debugArtifacts for details."
            ),
            "debugArtifacts": debug_artifacts[:10],
        }
        print(json.dumps(out), file=sys.stderr)
        return 2

    return 0


if __name__ == '__main__':
    sys.exit(main())
