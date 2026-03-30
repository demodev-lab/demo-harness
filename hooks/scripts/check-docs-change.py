#!/usr/bin/env python3

import json
import sys


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


def _normalize_path(value: str) -> str:
    if not isinstance(value, str):
        return ""
    p = value.strip().strip("\t\n\r \"'`()").strip()
    if not p:
        return ""
    p = p.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p


def _as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, str):
        return [_normalize_path(value)]
    if isinstance(value, list):
        return [_normalize_path(v) for v in value if isinstance(v, str)]
    return []


def _collect_paths(tool_input: dict) -> list:
    if not isinstance(tool_input, dict):
        return []

    candidates = [
        tool_input.get("file_path"),
        tool_input.get("path"),
        tool_input.get("cwd"),
        tool_input.get("working_directory"),
        tool_input.get("changed_files"),
        tool_input.get("files"),
        tool_input.get("file_paths"),
        tool_input.get("targets"),
        tool_input.get("path_list"),
    ]

    seen = set()
    out = []
    for item in candidates:
        for p in _as_list(item):
            if not p or not isinstance(p, str):
                continue
            if p not in seen:
                seen.add(p)
                out.append(p)

    if not out:
        if isinstance(tool_input, dict):
            for k, v in tool_input.items():
                if not isinstance(v, str) or not v.strip():
                    continue
                if any(ch in v for ch in ['/', '.', '.py', '.json', '.yml', '.yaml']):
                    if v not in seen and '\t' not in v:
                        seen.add(v)
                        out.append(v)

    return out


def _is_api_contract_path(path: str) -> bool:
    if not isinstance(path, str):
        return False

    lower_path = path.lower().strip()
    if not lower_path:
        return False

    api_extensions = ('.yaml', '.yml', '.graphql', '.proto')
    json_contract_files = {'openapi.json', 'swagger.json', 'api-schema.json', 'schema.json', 'spec.json'}
    path_patterns = ['routes/', 'api/', 'schema/', 'models/', 'types/', 'contracts/', 'migrations/']
    name_patterns = ['openapi', 'swagger', 'schema', 'api-contract', 'graphql', 'protobuf', 'grpc']

    if lower_path.split('/')[-1] in json_contract_files:
        return True

    basename = lower_path.rsplit('/', 1)[-1]
    if basename in {'openapi.json', 'swagger.json'}:
        return True

    if any(pattern in lower_path for pattern in path_patterns):
        return any(lower_path.endswith(ext) for ext in api_extensions) or any(p in basename for p in name_patterns)

    if any(pattern in basename for pattern in name_patterns):
        return True

    if any(lower_path.endswith(ext) for ext in api_extensions):
        return True

    return False


def main():
    try:
        payload = sys.stdin.read()
        data = json.loads(payload)
    except (json.JSONDecodeError, Exception):
        sys.exit(0)

    raw_tool_input = data.get("tool_input", {}) if isinstance(data, dict) else {}
    tool_input = _extract_payload(raw_tool_input)
    paths = _collect_paths(tool_input)

    if not paths:
        return 0

    matched = [p for p in paths if _is_api_contract_path(p)]
    if not matched:
        return 0

    message = {
        "systemMessage": (
            "API/contract-related file change detected: "
            f"{', '.join(matched)}. "
            "Please confirm related docs (README, OpenAPI spec, wiki, inline docs) are updated."
        )
    }
    print(json.dumps(message), file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
