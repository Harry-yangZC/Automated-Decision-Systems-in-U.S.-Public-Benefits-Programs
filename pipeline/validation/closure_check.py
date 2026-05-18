"""Phase 1 closure check.

Implements V2 §5.5's design-phase gate: every `[[slot:<path>|...]]` reference
in pipeline/gold_letters/MA_SNAP.annotated.md must resolve to a populated,
non-null path in the joined `(state_law, agency_program)` playbook, and
every `[[module:<id>|...]]` reference must have a corresponding file at
pipeline/request_modules/<id>.yaml.

Slots in the `_letter_meta.*` namespace are per-letter parameters and are
exempt: they live with the Phase 4 snapshot json, not the playbook.

Exits non-zero on any failure. Designed to be run from the repo root.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ANNOTATED = REPO_ROOT / "pipeline" / "gold_letters" / "MA_SNAP.annotated.md"
STATE_LAW = REPO_ROOT / "pipeline" / "playbook" / "state_law" / "MA.json"
AGENCY_PROGRAM = REPO_ROOT / "pipeline" / "playbook" / "agency_program" / "MA_SNAP.json"
MODULES_DIR = REPO_ROOT / "pipeline" / "request_modules"

SLOT_RE = re.compile(r"\[\[slot:([^|\]]+)\|")
MODULE_RE = re.compile(r"\[\[module:([^|\]]+)\|")
LIST_INDEX_RE = re.compile(r"^([^\[]+)\[(\d+)\]$")
FENCED_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]*`")


def strip_code(text: str) -> str:
    """Remove fenced and inline code spans so doc-example references inside
    backticks aren't treated as live slot/module references."""
    text = FENCED_BLOCK_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    return text


def load_joined() -> dict:
    state_law = json.loads(STATE_LAW.read_text())
    agency_program = json.loads(AGENCY_PROGRAM.read_text())
    return {"state_law": state_law, "agency_program": agency_program}


def resolve(joined: dict, path: str):
    """Resolve a dotted path against the joined playbook.

    Supports `foo.bar` and `foo.bar[N]` syntax. Returns a sentinel `_MISSING`
    when the path doesn't exist; returns the literal value (including `None`)
    when the path exists.
    """
    node = joined
    parts = path.split(".")
    for raw in parts:
        m = LIST_INDEX_RE.match(raw)
        if m:
            key, idx = m.group(1), int(m.group(2))
            if not isinstance(node, dict) or key not in node:
                return "_MISSING"
            node = node[key]
            if not isinstance(node, list) or idx >= len(node):
                return "_MISSING"
            node = node[idx]
        else:
            if not isinstance(node, dict) or raw not in node:
                return "_MISSING"
            node = node[raw]
    return node


def main() -> int:
    raw = ANNOTATED.read_text()
    text = strip_code(raw)
    slots = sorted(set(SLOT_RE.findall(text)))
    modules = sorted(set(MODULE_RE.findall(text)))

    joined = load_joined()

    slot_failures: list[tuple[str, str]] = []
    slot_passes = 0
    letter_meta_count = 0

    for slot in slots:
        if slot.startswith("_letter_meta."):
            letter_meta_count += 1
            continue
        val = resolve(joined, slot)
        if val == "_MISSING":
            slot_failures.append((slot, "path does not exist in playbook"))
        elif val is None:
            slot_failures.append((slot, "path resolves to null"))
        elif isinstance(val, (list, dict)) and not val:
            slot_failures.append((slot, "path resolves to empty container"))
        else:
            slot_passes += 1

    module_failures: list[str] = []
    module_passes = 0
    for mod in modules:
        path = MODULES_DIR / f"{mod}.yaml"
        if path.exists():
            module_passes += 1
        else:
            module_failures.append(mod)

    print("=" * 72)
    print("Phase 1 closure check  (V2 §5.5)")
    print("=" * 72)
    print(f"Annotated letter: {ANNOTATED.relative_to(REPO_ROOT)}")
    print(f"Playbook state_law: {STATE_LAW.relative_to(REPO_ROOT)}")
    print(f"Playbook agency_program: {AGENCY_PROGRAM.relative_to(REPO_ROOT)}")
    print(f"Modules directory: {MODULES_DIR.relative_to(REPO_ROOT)}")
    print()
    print(f"Slot references found: {len(slots)}")
    print(f"  playbook slots resolved: {slot_passes}")
    print(f"  _letter_meta.* (exempt): {letter_meta_count}")
    print(f"  failures: {len(slot_failures)}")
    print()
    print(f"Module references found: {len(modules)}")
    print(f"  modules with YAML file: {module_passes}")
    print(f"  missing module files: {len(module_failures)}")
    print()

    if slot_failures:
        print("--- SLOT FAILURES ---")
        for slot, reason in slot_failures:
            print(f"  FAIL {slot:60} {reason}")
        print()

    if module_failures:
        print("--- MODULE FAILURES ---")
        for mod in module_failures:
            print(f"  FAIL no file at request_modules/{mod}.yaml")
        print()

    ok = not (slot_failures or module_failures)
    if ok:
        print("PASS  Phase 1 closure check is GREEN. Gate to Phase 2 is open.")
        return 0
    else:
        print("FAIL  Phase 1 closure check has unresolved slots or modules.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
