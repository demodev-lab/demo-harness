#!/usr/bin/env bash
set -euo pipefail

# Robust destructive-command guard with fallback behavior.
if command -v python3 >/dev/null 2>&1; then
  python3 "$(dirname "$0")/block-destructive.py"
  exit $?
fi

# Fallback: legacy regex path (very conservative) in environments without python3.
INPUT="$(cat)"
COMMAND="$(printf '%s' "$INPUT" | sed -n 's/.*\"command\"[[:space:]]*:[[:space:]]*\"\(.*\)\".*/\1/p' | head -n 1)"

# trim wrapping whitespace/quotes and strip quotes to reduce false misses
COMMAND="$(printf '%s' "$COMMAND" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | tr -d '"' | tr -d "'")"

if printf '%s' "$COMMAND" | grep -Eiq '(^|[;(&|])\s*rm(\s+-[^[:space:]]+){0,6}\s+/' \
    || printf '%s' "$COMMAND" | grep -Eiq '\bgit\s+clean\b|\bgit\s+push\b.*--force|\bgit\s+push\b.* -f|\bDROP[[:space:]]+(TABLE|DATABASE)|mkfs\.|dd[[:space:]]+if=' >/dev/null; then
  printf '{"hookSpecificOutput":{"permissionDecision":"deny"},"decision":"block","reason":"Destructive command blocked by fallback matcher"}\n' >&2
  exit 2
fi

exit 0
