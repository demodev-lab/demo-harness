#!/usr/bin/env python3
"""PostToolUse(Bash) hook: track repeated errors and suggest /rule-promote."""
import sys
import json
import hashlib
import os
import re
import time

REPEAT_THRESHOLD = 3
EXPIRY_SECONDS = 3600  # 1 hour window

def _get_tracker_path():
    cwd_hash = hashlib.md5(os.getcwd().encode()).hexdigest()[:8]
    return f"/tmp/.harness-error-tracker-{cwd_hash}.json"

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

def load_log():
    try:
        with open(_get_tracker_path(), "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_log(log):
    try:
        with open(_get_tracker_path(), "w") as f:
            json.dump(log, f)
    except OSError:
        pass

def clean_expired(log):
    now = time.time()
    return {k: v for k, v in log.items() if now - v.get("last", 0) < EXPIRY_SECONDS}

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

    sig_hash = hashlib.md5(sig.encode()).hexdigest()[:12]

    log = clean_expired(load_log())
    entry = log.get(sig_hash, {"count": 0, "sig": sig, "last": 0})
    entry["count"] += 1
    entry["last"] = time.time()
    log[sig_hash] = entry
    save_log(log)

    if entry["count"] >= REPEAT_THRESHOLD:
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
