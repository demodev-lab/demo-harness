"""
Harness config loader — reads .harness.json with fallback to defaults.

Import fallback pattern (MUST use in all hook scripts):
    try:
        from lib.config_loader import load_config
    except ImportError:
        def load_config(_):
            return DEFAULT_CONFIG
"""
import json
import os
import sys

DEFAULT_CONFIG = {
    "staleness_weeks": 8,
    "agents_md_max_lines": 60,
    "max_distinct_rules": 15,
    "repeat_threshold": 3,
    "error_expiry_days": 7,
    "file_change_threshold": 10,
    "suggestion_cooldown_seconds": 300,
    "session_window_seconds": 1800,
    "failure_log_path": "docs/failure-log.md",
    "state_file_path": "docs/.harness-state.json",
}


def load_config(project_root: str) -> dict:
    """Load .harness.json from project root, falling back to defaults."""
    config_path = os.path.join(project_root, ".harness.json")
    if not os.path.isfile(config_path):
        return dict(DEFAULT_CONFIG)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[harness] Warning: failed to parse .harness.json: {e}", file=sys.stderr)
        return dict(DEFAULT_CONFIG)

    merged = dict(DEFAULT_CONFIG)
    for key in DEFAULT_CONFIG:
        if key in user_config:
            merged[key] = user_config[key]
    return merged


def get_project_root() -> str:
    """Find project root by walking up from cwd looking for .git or .harness.json."""
    current = os.getcwd()
    for _ in range(20):
        if os.path.isdir(os.path.join(current, ".git")) or os.path.isfile(
            os.path.join(current, ".harness.json")
        ):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.getcwd()
