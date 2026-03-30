#!/usr/bin/env python3

import json
import os
import sys
from pathlib import Path


REQUIRED_FILES = [
    '.claude-plugin/plugin.json',
    'hooks/hooks.json',
    'hooks/scripts/block-destructive.sh',
    'hooks/scripts/block-destructive.py',
    'hooks/scripts/check-docs-change.py',
    'hooks/scripts/completion-gate.py',
    'hooks/scripts/harness-hook-selftest.py',
    'hooks/scripts/validate-harness-integrity.py',
    'skills/harness-init/references/agents-md-template.md',
    'skills/harness-init/references/glossary-template.md',
    'skills/harness-init/references/failure-log-template.md',
    'skills/harness-init/references/skill-template.md',
    'skills/harness-init/references/hooks-template.json',
    'skills/harness-init/references/completion-checklist-template.md',
    'skills/harness-init/references/weekly-review-template.md',
    'skills/harness-init/references/postmortem-template.md',
    'skills/harness-init/references/architecture-notes-template.md',
    'skills/harness-init/references/operating-principles-template.md',
    'skills/harness-init/references/onboarding-sequence.md',
    'skills/harness-init/references/hook-checklist-template.md',
]


def fail(msg, code=2):
    print(msg)
    return code


def check_json(path: Path, issues: list):
    try:
        with path.open('r', encoding='utf-8') as fp:
            json.load(fp)
    except Exception as e:
        issues.append(f"JSON parse failed: {path} ({e})")


def check_paths(root: Path):
    missing = []
    for rel in REQUIRED_FILES:
        p = root / rel
        if not p.exists():
            missing.append(str(rel))
    return missing


def check_hook_commands(root: Path, issues: list):
    hooks = root / 'hooks' / 'hooks.json'
    if not hooks.exists():
        issues.append('hooks/hooks.json missing')
        return

    try:
        data = json.loads(hooks.read_text(encoding='utf-8'))
    except Exception:
        issues.append('hooks/hooks.json not parseable')
        return

    import re

    hooks_data = data.get('hooks', {})
    if not isinstance(hooks_data, dict):
        issues.append('hooks/hooks.json: "hooks" must be an object')
        return

    script_deps = []
    for event_name, event_defs in hooks_data.items():
        if not isinstance(event_defs, list):
            issues.append(f'hooks/hooks.json: event "{event_name}" must be list')
            continue
        for entry in event_defs:
            for h in entry.get('hooks', []) if isinstance(entry, dict) else []:
                if h.get('type') == 'command' and isinstance(h.get('command'), str):
                    cmd = h['command']
                    # Extract paths using explicit CLAUDE_PLUGIN_ROOT expansion.
                    root_refs = re.findall(r'\$\{CLAUDE_PLUGIN_ROOT\}(/[^"\'\'\s;]*)', cmd)
                    if not root_refs:
                        matches = re.findall(r'(["\'](?:/)?[\w./-]*/hooks/scripts/[^"\'\s]+["\'])', cmd)
                        root_refs = [m.strip('"\'') for m in matches]
                    for rel in root_refs:
                        rel = rel.lstrip('/')
                        rel = rel.split()[0] if ' ' in rel else rel
                        rel = rel.split('"')[0].split('\'')[0]
                        ref = root / rel
                        if rel and not ref.exists():
                            script_deps.append((cmd, str(ref)))

    if script_deps:
        for cmd, path in script_deps:
            issues.append(f'hooks command reference missing file for "{cmd}" -> {path}')


def check_executability(root: Path, issues: list):
    exec_candidates = [
        root / 'hooks' / 'scripts' / 'block-destructive.sh',
        root / 'hooks' / 'scripts' / 'completion-gate.py',
        root / 'hooks' / 'scripts' / 'block-destructive.py',
        root / 'hooks' / 'scripts' / 'check-docs-change.py',
        root / 'hooks' / 'scripts' / 'harness-hook-selftest.py',
        root / 'hooks' / 'scripts' / 'validate-harness-integrity.py',
    ]
    for p in exec_candidates:
        if not p.exists():
            continue
        if not os.access(p, os.X_OK):
            issues.append(f'Executable bit missing: {p}')


def check_harness_init_template_references(root: Path, issues: list):
    harness_init_skill = root / 'skills' / 'harness-init' / 'SKILL.md'
    if not harness_init_skill.exists():
        issues.append('skills/harness-init/SKILL.md missing (cannot validate references)')
        return

    text = harness_init_skill.read_text(encoding='utf-8')
    required_refs = {
        'agents-md-template.md',
        'glossary-template.md',
        'failure-log-template.md',
        'skill-template.md',
        'hooks-template.json',
        'completion-checklist-template.md',
        'weekly-review-template.md',
        'postmortem-template.md',
        'architecture-notes-template.md',
        'operating-principles-template.md',
    }

    missing = []
    for ref in sorted(required_refs):
        if ref not in text:
            missing.append(ref)

    if missing:
        issues.append(f'harness-init SKILL.md missing template references: {", ".join(missing)}')


def check_frontmatter_in_skills(root: Path, issues: list):
    for skill in sorted((root / 'skills').glob('*/SKILL.md')):
        lines = skill.read_text(encoding='utf-8').splitlines()
        if not lines or lines[0].strip() != '---':
            issues.append(f'{skill.as_posix()} lacks frontmatter start ---')
            continue
        # Find ending ---
        try:
            end = lines[1:].index('---')
        except ValueError:
            issues.append(f'{skill.as_posix()} lacks frontmatter end ---')
            continue
        fm = lines[1:1+end]
        keys = {}
        for l in fm:
            if ':' not in l:
                continue
            k, v = l.split(':', 1)
            keys[k.strip().lower()] = v.strip()
        for k in ['name', 'description']:
            if k not in keys:
                issues.append(f'{skill.as_posix()} missing frontmatter key: {k}')


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())

    issues = []
    missing = check_paths(root)
    issues.extend([f'missing required file: {m}' for m in missing])

    if not missing:
        check_json(root / 'hooks' / 'hooks.json', issues)
        check_json(root / '.claude-plugin' / 'plugin.json', issues)

    check_hook_commands(root, issues)
    check_executability(root, issues)
    check_harness_init_template_references(root, issues)
    check_frontmatter_in_skills(root, issues)

    if issues:
        print('HARNESS INTEGRITY CHECK: FAILED')
        for issue in issues:
            print(f'- {issue}')
        return 2

    print('HARNESS INTEGRITY CHECK: OK')
    print(f'Checked {len(REQUIRED_FILES)} required files + skills/frontmatter/hook references')
    return 0


if __name__ == '__main__':
    sys.exit(main())
