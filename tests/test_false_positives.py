#!/usr/bin/env python3
"""AC-19: False-positive corpus test for suggest-failure-absorb.py.

Reads each corpus file, pipes it as {"tool_result": "..."} to suggest-failure-absorb.py,
checks if stderr contains "Harness", and compares against expected-results.json.
"""
import json
import subprocess
import sys
from pathlib import Path

CORPUS_DIR = Path(__file__).resolve().parent / "corpus"
SCRIPT = Path(__file__).resolve().parent.parent / "hooks" / "scripts" / "suggest-failure-absorb.py"
EXPECTED_FILE = CORPUS_DIR / "expected-results.json"


def run_script(content: str) -> str:
    payload = json.dumps({"tool_result": content})
    p = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=payload,
        text=True,
        capture_output=True,
        check=False,
    )
    return p.stderr


def main() -> int:
    with open(EXPECTED_FILE, encoding="utf-8") as f:
        expected = json.load(f)

    passed = 0
    failed = 0

    for category, files in expected.items():
        corpus_subdir = CORPUS_DIR / category
        for filename, should_trigger in files.items():
            file_path = corpus_subdir / filename
            if not file_path.is_file():
                print(f"[SKIP] {category}/{filename}: file not found")
                continue

            content = file_path.read_text(encoding="utf-8")
            stderr = run_script(content)
            did_trigger = "Harness" in stderr

            if did_trigger == should_trigger:
                print(f"[PASS] {category}/{filename}")
                passed += 1
            else:
                expected_str = "trigger" if should_trigger else "silent"
                actual_str = "trigger" if did_trigger else "silent"
                print(f"[FAIL] {category}/{filename}: expected={expected_str}, actual={actual_str}")
                if stderr:
                    print(f"  stderr={stderr[:200]!r}")
                failed += 1

    print()
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed} total")

    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
