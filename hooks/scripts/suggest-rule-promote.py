#!/usr/bin/env python3
"""PostToolUse(Bash) hook: track repeated errors and suggest /rule-promote."""
import sys
import json
import hashlib
import os
import re
import time

try:
    from lib.config_loader import load_config, get_project_root
except ImportError:
    def load_config(_):
        return {"repeat_threshold": 3, "error_expiry_days": 7}
    def get_project_root():
        return os.getcwd()

try:
    from lib.state_manager import load_state, buffer_state
except ImportError:
    def load_state(_):
        return {"error_tracker": {}}
    def buffer_state(_):
        pass

ERROR_SIGNATURES = [
    r'(FAIL\w*:?\s+.{10,60})',
    r'(Error:\s+.{10,60})',
    r'(AssertionError:\s+.{10,60})',
    r'(TypeError:\s+.{10,60})',
    r'(ReferenceError:\s+.{10,60})',
    r'(SyntaxError:\s+.{10,60})',
    r'(ModuleNotFoundError:\s+.{10,60})',
    r'(ImportError:\s+.{10,60})',
]


def extract_error_signature(output):
    for pat in ERROR_SIGNATURES:
        match = re.search(pat, output, re.IGNORECASE)
        if match:
            sig = re.sub(r'\d+', 'N', match.group(1).strip())
            sig = re.sub(r'/\S+/', '/PATH/', sig)
            return sig
    return None


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    output = data.get("tool_result", "") or data.get("tool_response", "") or ""
    if isinstance(output, dict):
        output = json.dumps(output)

    if not output or len(output) < 10:
        sys.exit(0)

    sig = extract_error_signature(output)
    if not sig:
        sys.exit(0)

    root = get_project_root()
    config = load_config(root)
    state = load_state(root)

    repeat_threshold = config["repeat_threshold"]
    expiry_seconds = config["error_expiry_days"] * 86400

    sig_hash = hashlib.md5(sig.encode()).hexdigest()[:12]
    tracker = dict(state.get("error_tracker", {}))

    # Clean expired entries
    now = time.time()
    tracker = {k: v for k, v in tracker.items() if now - v.get("last", 0) < expiry_seconds}

    entry = tracker.get(sig_hash, {"count": 0, "sig": sig, "last": 0})
    entry = dict(entry)
    entry["count"] += 1
    entry["last"] = now
    tracker[sig_hash] = entry

    # Buffer state change (flushed at session end by Stop hook)
    buffer_state({"error_tracker": tracker})

    if entry["count"] >= repeat_threshold:
        msg = {
            "systemMessage": (
                f"[Harness] Same error detected {entry['count']} times: \"{sig[:80]}\". "
                "Consider running /rule-promote to convert the related text rule "
                "into an automated hook for mechanical prevention."
            )
        }
        sys.stderr.write(json.dumps(msg))

    sys.exit(0)

if __name__ == "__main__":
    main()
