"""Phase 2 closure check.

Implements the three audits described in V2 Phase 2 plan §A.4:

  1. Schema conformance — every entry in question_spec.yaml validates
     against pipeline/schemas/question_spec.schema.yaml (Draft-07).
  2. Forward closure — every web-extractable leaf path in the joined
     (state_law, agency_program) playbook is either covered by a
     question_spec entry, or appears in EXCLUDED_PATHS with a documented
     reason.
  3. Reverse closure — every field_path in question_spec.yaml resolves to
     a leaf in the joined playbook. For entries whose answer_format is
     `not_available`, a null resolution is acceptable (the question is
     designed to test the abstention sentinel); for all other entries the
     resolved value must be non-null.

Exits non-zero on any failure. Designed to be run from the repo root.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC = REPO_ROOT / "pipeline" / "questions" / "question_spec.yaml"
SCHEMA = REPO_ROOT / "pipeline" / "schemas" / "question_spec.schema.yaml"
STATE_LAW = REPO_ROOT / "pipeline" / "playbook" / "state_law" / "MA.json"
AGENCY_PROGRAM = REPO_ROOT / "pipeline" / "playbook" / "agency_program" / "MA_SNAP.json"

LIST_INDEX_RE = re.compile(r"^([^\[]+)\[(\d+)\]$")

# Field names skipped automatically when walking the playbook.
META_FIELDS = {
    "evidence",
    "confidence",
    "needs_manual_review",
    "_reserved_for_campaign_tracking",
}
# Top-of-section identity fields skipped automatically.
ADMIN_TOP = {"state", "program"}

# Paths that exist in the playbook but should NOT have a question_spec
# entry. Each value is the documented reason.
_PRR = "state_law.public_records_law"
_AP = "agency_program"
_BT0 = f"{_AP}.benefits_tech_systems[0]"
_BT1 = f"{_AP}.benefits_tech_systems[1]"
_PARAPHRASE = (
    "long paraphrase; answer_format=paraphrase; Phase 4 reads directly"
)
_PRODUCTION_DOC = (
    "deep production-doc fact; playbook-only per Phase 2 plan"
)

EXCLUDED_PATHS: dict[str, str] = {
    f"{_PRR}.record_definition": _PARAPHRASE,
    f"{_PRR}.segregation_clause": _PARAPHRASE,
    f"{_PRR}.state_specific_quirks": (
        "list of paraphrases; answer_format=paraphrase; "
        "Phase 4 reads directly"
    ),
    f"{_PRR}.extension.agency_initial_basis": (
        "long paraphrase; answer_format=paraphrase; "
        "companion to extension.agency_initial_days"
    ),
    f"{_PRR}.extension.supervisor_extension_basis": (
        "long paraphrase; answer_format=paraphrase; "
        "companion to extension.supervisor_extension_days"
    ),
    f"{_PRR}.fee_waiver.required_assertions": (
        "list of paraphrase assertions; answer_format=paraphrase; "
        "Phase 4 reads directly"
    ),
    f"{_PRR}.appeal_path.deadline_unit": (
        "composed into appeal_path.deadline_days ground_truth "
        "(e.g., '90 calendar days')"
    ),
    f"{_AP}.contact.city": (
        "composed into contact.address_line1 ground_truth "
        "(street, city, state)"
    ),
    f"{_AP}.contact.state": (
        "composed into contact.address_line1 ground_truth; "
        "redundant with playbook state field"
    ),
    f"{_PRR}.expedited_processing.statutory_citation": (
        "expedited_processing.available=false in MA; "
        "citation is null by construction"
    ),
    f"{_PRR}.expedited_processing.criteria": (
        "expedited_processing.available=false in MA; "
        "criteria is [] by construction"
    ),
    f"{_PRR}.certification_text": (
        "certification_required=false in MA; "
        "certification_text is null by construction"
    ),
    f"{_AP}.contact.address_line2": (
        "MA DTA address has no line 2; null by construction"
    ),
    f"{_AP}.keywords": (
        "drafting-side keyword bag; not a fact to certify"
    ),
    f"{_BT0}.contract_or_order_ids": _PRODUCTION_DOC,
    f"{_BT0}.pricing_terms": _PRODUCTION_DOC,
    f"{_BT0}.user_seats": _PRODUCTION_DOC,
    f"{_BT0}.batch_or_match_limits": _PRODUCTION_DOC,
    f"{_BT0}.required_data_inputs": _PRODUCTION_DOC,
    f"{_BT0}.named_deliverables": _PRODUCTION_DOC,
    f"{_BT0}.hosting_security_retention": _PRODUCTION_DOC,
    f"{_BT1}.contract_or_order_ids": _PRODUCTION_DOC,
    f"{_BT1}.pricing_terms": _PRODUCTION_DOC,
    f"{_BT1}.user_seats": _PRODUCTION_DOC,
    f"{_BT1}.batch_or_match_limits": _PRODUCTION_DOC,
    f"{_BT1}.required_data_inputs": _PRODUCTION_DOC,
    f"{_BT1}.named_deliverables": _PRODUCTION_DOC,
    f"{_BT1}.hosting_security_retention": _PRODUCTION_DOC,
}


def load_joined() -> dict:
    state_law = json.loads(STATE_LAW.read_text())
    agency_program = json.loads(AGENCY_PROGRAM.read_text())
    return {"state_law": state_law, "agency_program": agency_program}


def resolve(joined: dict, path: str):
    """Resolve a dotted path; returns `_MISSING` if no such path."""
    node = joined
    for raw in path.split("."):
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


def walk_section(section_node: dict, section_name: str):
    """Yield dotted paths for every web-extractable leaf in the section.

    Skips meta fields (evidence/confidence/needs_manual_review/_reserved...)
    and top-of-section identity fields (state, program). Lists of dicts
    are enumerated as `[N]`; lists of primitives are treated as leaves.
    """

    def _walk(node, prefix: str):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in META_FIELDS:
                    continue
                if prefix == section_name and k in ADMIN_TOP:
                    continue
                yield from _walk(v, f"{prefix}.{k}")
        elif isinstance(node, list) and node and isinstance(node[0], dict):
            for i, item in enumerate(node):
                yield from _walk(item, f"{prefix}[{i}]")
        else:
            yield prefix

    yield from _walk(section_node, section_name)


def audit_schema_conformance(spec: list[dict], schema: dict) -> list[str]:
    validator = Draft7Validator(schema)
    failures: list[str] = []
    for i, entry in enumerate(spec):
        for err in validator.iter_errors(entry):
            failures.append(f"entry[{i}] field_path={entry.get('field_path')!r}: {err.message}")
    return failures


def audit_forward_closure(spec: list[dict], joined: dict) -> list[str]:
    covered = {e["field_path"] for e in spec}
    expected: list[str] = []
    for section_name in ("state_law", "agency_program"):
        expected.extend(walk_section(joined[section_name], section_name))
    failures: list[str] = []
    for path in expected:
        if path in covered:
            continue
        if path in EXCLUDED_PATHS:
            continue
        failures.append(f"uncovered playbook leaf: {path}")
    for path in EXCLUDED_PATHS:
        if path not in expected:
            failures.append(f"stale exclusion (path not in playbook): {path}")
    return failures


def audit_reverse_closure(spec: list[dict], joined: dict) -> list[str]:
    failures: list[str] = []
    for entry in spec:
        fp = entry["field_path"]
        val = resolve(joined, fp)
        if val == "_MISSING":
            failures.append(f"field_path does not resolve: {fp}")
            continue
        if val is None:
            if entry["answer_format"] != "not_available":
                failures.append(
                    f"field_path resolves to null but answer_format is "
                    f"{entry['answer_format']!r} (expected 'not_available'): {fp}"
                )
            continue
        if isinstance(val, (list, dict)) and not val:
            failures.append(f"field_path resolves to empty container: {fp}")
    return failures


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    schema = yaml.safe_load(SCHEMA.read_text())
    joined = load_joined()

    schema_failures = audit_schema_conformance(spec, schema)
    forward_failures = audit_forward_closure(spec, joined)
    reverse_failures = audit_reverse_closure(spec, joined)

    print("=" * 72)
    print("Phase 2 closure check  (V2 §6.1 / Phase 2 plan §A.4)")
    print("=" * 72)
    print(f"Spec:     {SPEC.relative_to(REPO_ROOT)}")
    print(f"Schema:   {SCHEMA.relative_to(REPO_ROOT)}")
    print(f"Playbook: {STATE_LAW.relative_to(REPO_ROOT)},")
    print(f"          {AGENCY_PROGRAM.relative_to(REPO_ROOT)}")
    print()
    print(f"Spec entries: {len(spec)}")
    print(f"EXCLUDED_PATHS: {len(EXCLUDED_PATHS)}")
    print()
    print(f"Schema conformance failures: {len(schema_failures)}")
    print(f"Forward closure failures:    {len(forward_failures)}")
    print(f"Reverse closure failures:    {len(reverse_failures)}")
    print()

    if schema_failures:
        print("--- SCHEMA CONFORMANCE FAILURES ---")
        for f in schema_failures:
            print(f"  FAIL {f}")
        print()

    if forward_failures:
        print("--- FORWARD CLOSURE FAILURES ---")
        for f in forward_failures:
            print(f"  FAIL {f}")
        print()

    if reverse_failures:
        print("--- REVERSE CLOSURE FAILURES ---")
        for f in reverse_failures:
            print(f"  FAIL {f}")
        print()

    ok = not (schema_failures or forward_failures or reverse_failures)
    if ok:
        print("PASS  Phase 2 closure check is GREEN. Gate to Phase 3 is open.")
        return 0
    else:
        print("FAIL  Phase 2 closure check has unresolved issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
