#!/usr/bin/env python3

import json
import re
import sys


def load_command(payload_text: str) -> str:
    """Load input payload and extract the command string from Claude hook JSON."""
    try:
        data = json.loads(payload_text)
    except Exception:
        return ""

    # Claude hooks usually provide command under tool_input.command.
    # fallback to common variants just in case.
    tool_input = data.get("tool_input", {}) if isinstance(data, dict) else {}
    for path in [
        ("tool_input", "command"),
        ("tool_input", "command_text"),
        ("tool_input", "cmd"),
        ("tool_input", "input"),
        ("input", "command"),
        ("input", "command_text"),
        ("input", "cmd"),
        ("command",),
        ("action", "command"),
    ]:
        current = data
        for key in path:
            if not isinstance(current, dict) or key not in current:
                current = None
                break
            current = current[key]
        if isinstance(current, str) and current.strip():
            return current.strip()

    # handle legacy wrapper formats that wrap JSON in "tool_input": "{\"command\":...}"
    command_field = data.get("tool_input") if isinstance(data.get("tool_input"), str) else None
    if isinstance(command_field, str):
        try:
            nested = json.loads(command_field)
            if isinstance(nested, dict):
                nested_cmd = nested.get("command")
                if isinstance(nested_cmd, str) and nested_cmd.strip():
                    return nested_cmd.strip()
        except Exception:
            pass

    return ""


def normalize(command: str) -> str:
    command = command.strip()
    # Preserve for message, normalize for matching.
    return " ".join(command.lower().split())


def match_pattern(command: str):
    # Strict but useful regexes with anchors for destructive paths, while avoiding common false positives.
    patterns = [
        # rm -rf on root or absolute path, or rm -rf target recursively under /tmp etc.
        (r"(?:^|[;(&|])\s*rm\s+(-[rf]+\s+)?-rf\s+/(?:[^\s]*|\\$\{[^}]+\})", "rm -rf /"),
        (r"(^|[;(&|])\s*rm\s+(-[rf]+\s+)?-rf\s+\*", "rm -rf *"),
        (r"(^|[;(&|])\s*rm\s+(-[rf]+\s+)?-rf\s+\$\{[^}]+\}", "rm -rf ${...}"),
        # common destructive git operations
        (r"\bgit\s+push\b[^\n]*\s+--force\b", "git push --force"),
        (r"\bgit\s+push\b[^\n]*\s+-f\b", "git push -f"),
        (r"\bgit\s+reset\s+--hard\b", "git reset --hard"),
        (r"\bgit\s+clean\b[^\n]*-[fdxX]+", "git clean -fdx"),
        (r"\bchown\s+[^\n]*\s+root(:|/?)root\b", "chown root root"),
        (r"\bchmod\s+[^\n]*\b777\b", "chmod 777"),
        (r"\bdrop\s+table\b", "DROP TABLE"),
        (r"\bdrop\s+database\b", "DROP DATABASE"),
        (r"\bmkfs(\.[a-zA-Z0-9]+)?\b", "mkfs"),
        (r"\bdd\b[^\n]*\bif=/dev/(sd|hd|nvme|vd)", "dd if=/dev/*"),
        (r"\b>\s*/dev/(sd|hd|nvme|vd)", "dd-like redirect to /dev/*"),
        (r"\b:\s*\(\)\s*\{", "fork bomb"),
    ]

    for pattern, reason in patterns:
        if re.search(pattern, command):
            return reason
    return None


def main() -> int:
    payload = sys.stdin.read()
    command = load_command(payload)

    if not command:
        # Nothing to analyze.
        return 0

    normalized = normalize(command)
    reason = match_pattern(normalized)

    if reason:
        out = {
            "hookSpecificOutput": {
                "permissionDecision": "deny",
                "decision": "block",
                "reason": f"Destructive command blocked: {reason}",
            }
        }
        print(json.dumps(out), file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
