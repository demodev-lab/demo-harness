#!/usr/bin/env python3
"""PostToolUse(Edit|Write) hook: detect large changes and suggest /harness-audit."""
import sys
import json
import os
import time

try:
    from lib.config_loader import load_config, get_project_root
except ImportError:
    def load_config(_):
        return {"file_change_threshold": 10, "session_window_seconds": 1800,
                "suggestion_cooldown_seconds": 300}
    def get_project_root():
        return os.getcwd()

try:
    from lib.state_manager import load_state, buffer_state
except ImportError:
    def load_state(_):
        return {"file_change_tracker": {"files": [], "last_suggest": 0}}
    def buffer_state(_):
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

    root = get_project_root()
    config = load_config(root)
    state = load_state(root)

    now = time.time()
    tracker = dict(state.get("file_change_tracker", {"files": [], "last_suggest": 0}))
    session_window = config["session_window_seconds"]
    cooldown = config["suggestion_cooldown_seconds"]
    threshold = config["file_change_threshold"]

    # Clean expired file entries
    files = [f for f in tracker.get("files", []) if now - f.get("time", 0) < session_window]
    if not files:
        tracker["last_suggest"] = 0

    # Add new file if not already tracked
    if not any(f.get("path") == file_path for f in files):
        files.append({"path": file_path, "time": now})

    tracker["files"] = files
    unique_count = len(files)

    # Buffer state change
    buffer_state({"file_change_tracker": tracker})

    if unique_count >= threshold and (now - tracker.get("last_suggest", 0)) > cooldown:
        tracker["last_suggest"] = now
        buffer_state({"file_change_tracker": tracker})

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
