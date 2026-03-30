#!/usr/bin/env python3
"""PostToolUse(Edit|Write) hook: detect large changes and suggest /harness-audit."""
import sys
import json
import os
import time

CHANGE_LOG = "/tmp/.harness-change-tracker.json"
FILE_THRESHOLD = 10
SESSION_WINDOW = 1800  # 30 min session window
COOLDOWN = 300  # only suggest once per 5 minutes

def load_log():
    try:
        with open(CHANGE_LOG, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"files": [], "last_suggest": 0}

def save_log(log):
    try:
        with open(CHANGE_LOG, "w") as f:
            json.dump(log, f)
    except OSError:
        pass

def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        sys.exit(0)

    now = time.time()
    log = load_log()

    log["files"] = [
        f for f in log["files"]
        if now - f.get("time", 0) < SESSION_WINDOW
    ]

    if not any(f.get("path") == file_path for f in log["files"]):
        log["files"].append({"path": file_path, "time": now})

    unique_count = len(log["files"])
    save_log(log)

    if unique_count >= FILE_THRESHOLD and (now - log.get("last_suggest", 0)) > COOLDOWN:
        log["last_suggest"] = now
        save_log(log)
        msg = {
            "systemMessage": (
                f"[Harness] {unique_count} files modified in this session. "
                "Large changes increase risk of rule violations and documentation drift. "
                "Consider running /harness-audit to check for bloat, conflicts, and "
                "ensure documentation is up to date."
            )
        }
        sys.stderr.write(json.dumps(msg))

    sys.exit(0)

if __name__ == "__main__":
    main()
