"""
Harness state manager — persistent state with session buffering.

PostToolUse hooks call buffer_state() to accumulate changes in /tmp.
Stop hook calls flush_state() to merge buffer into docs/.harness-state.json.

Import fallback pattern (MUST use in all hook scripts):
    try:
        from lib.state_manager import load_state, buffer_state, flush_state
    except ImportError:
        def load_state(_): return dict(INITIAL_STATE)
        def buffer_state(_): pass
        def flush_state(_): return dict(INITIAL_STATE)
"""
import copy
import json
import os
import sys
import tempfile
import time

INITIAL_STATE = {
    "version": "2.0",
    "last_updated": None,
    "failures": {
        "total": 0,
        "by_category": {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0},
        "recent": [],
    },
    "absorptions": {
        "total": 0,
        "verified": 0,
        "pending_verification": [],
        "history": [],
    },
    "promotions": {
        "candidates": [],
        "completed": [],
        "rejected": [],
    },
    "reviews": {
        "last_review_date": None,
        "review_count": 0,
        "health_scores": [],
    },
    "error_tracker": {},
    "file_change_tracker": {"files": [], "last_suggest": 0},
    "suggestion_cooldowns": {},
}

MAX_RECENT = 50


def _buffer_path() -> str:
    return f"/tmp/.harness-session-{os.getpid()}.json"


def _deep_merge(base: dict, override: dict) -> dict:
    """Merge override into base, combining lists and dicts recursively."""
    result = copy.deepcopy(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        elif key in result and isinstance(result[key], list) and isinstance(val, list):
            result[key] = result[key] + val
        else:
            result[key] = copy.deepcopy(val)
    return result


# --- Core state I/O ---

def load_state(project_root: str) -> dict:
    """Load state from docs/.harness-state.json, returning INITIAL_STATE if missing."""
    state_path = os.path.join(project_root, "docs", ".harness-state.json")
    if not os.path.isfile(state_path):
        return copy.deepcopy(INITIAL_STATE)
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = copy.deepcopy(INITIAL_STATE)
        merged = _deep_merge(merged, data)
        return merged
    except (json.JSONDecodeError, OSError) as e:
        print(f"[harness] Warning: failed to read state: {e}", file=sys.stderr)
        return copy.deepcopy(INITIAL_STATE)


def save_state(project_root: str, state: dict) -> bool:
    """Atomic write state to docs/.harness-state.json."""
    state_path = os.path.join(project_root, "docs", ".harness-state.json")
    state_dir = os.path.dirname(state_path)

    new_state = copy.deepcopy(state)
    new_state["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Trim recent lists to MAX_RECENT
    if len(new_state.get("failures", {}).get("recent", [])) > MAX_RECENT:
        new_state["failures"]["recent"] = new_state["failures"]["recent"][-MAX_RECENT:]

    try:
        os.makedirs(state_dir, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=state_dir, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(new_state, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp_path, state_path)
        return True
    except OSError as e:
        print(f"[harness] Warning: failed to save state: {e}", file=sys.stderr)
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        return False


# --- Session buffering (PostToolUse hooks use these) ---

def buffer_state(state_delta: dict) -> None:
    """Append state delta to session buffer in /tmp. Does not touch docs/."""
    buf_path = _buffer_path()
    existing = []
    if os.path.isfile(buf_path):
        try:
            with open(buf_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, OSError):
            existing = []

    existing.append({"ts": time.time(), "delta": state_delta})
    try:
        with open(buf_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False)
    except OSError:
        pass


def flush_state(project_root: str) -> dict:
    """Merge session buffer into persistent state, then delete buffer."""
    state = load_state(project_root)
    buf_path = _buffer_path()

    if not os.path.isfile(buf_path):
        return state

    try:
        with open(buf_path, "r", encoding="utf-8") as f:
            deltas = json.load(f)
    except (json.JSONDecodeError, OSError):
        return state

    for entry in deltas:
        delta = entry.get("delta", {})
        state = _deep_merge(state, delta)

    save_state(project_root, state)

    try:
        os.unlink(buf_path)
    except OSError:
        pass

    return state


# --- Immutable state mutation helpers ---

def record_failure(state: dict, category: int, description: str, error_sig: str) -> dict:
    """Record a failure. Returns new state (immutable)."""
    new = copy.deepcopy(state)
    cat_key = str(category)
    new["failures"]["total"] += 1
    new["failures"]["by_category"][cat_key] = new["failures"]["by_category"].get(cat_key, 0) + 1
    new["failures"]["recent"].append({
        "date": time.strftime("%Y-%m-%d"),
        "description": description[:200],
        "category": category,
        "error_sig": error_sig[:100],
        "status": "pending",
    })
    return new


def record_absorption(state: dict, failure_id: str, layer: str, artifact: str) -> dict:
    """Record an absorption. Returns new state (immutable)."""
    new = copy.deepcopy(state)
    new["absorptions"]["total"] += 1
    new["absorptions"]["history"].append({
        "date": time.strftime("%Y-%m-%d"),
        "failure_id": failure_id,
        "layer": layer,
        "artifact": artifact,
        "verified": False,
    })
    return new


def add_promotion_candidate(state: dict, pattern: str, count: int, hook_type: str) -> dict:
    """Add a promotion candidate. Returns new state (immutable)."""
    new = copy.deepcopy(state)
    for candidate in new["promotions"]["candidates"]:
        if candidate.get("pattern") == pattern:
            candidate["count"] = count
            return new
    new["promotions"]["candidates"].append({
        "date": time.strftime("%Y-%m-%d"),
        "pattern": pattern[:200],
        "count": count,
        "hook_type": hook_type,
    })
    return new


def check_cooldown(state: dict, error_sig: str, cooldown_seconds: int) -> bool:
    """Return True if error_sig is still in cooldown (should be suppressed)."""
    last_time = state.get("suggestion_cooldowns", {}).get(error_sig, 0)
    return (time.time() - last_time) < cooldown_seconds


def update_suggestion_cooldown(state: dict, error_sig: str) -> dict:
    """Update cooldown timestamp for error_sig. Returns new state (immutable)."""
    new = copy.deepcopy(state)
    if "suggestion_cooldowns" not in new:
        new["suggestion_cooldowns"] = {}
    new["suggestion_cooldowns"][error_sig] = time.time()
    return new
