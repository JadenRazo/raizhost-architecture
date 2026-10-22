#!/usr/bin/env python3
"""Offline, conservative Terraform JSON triage. Never authorizes or runs an apply.

Only counts and fixed reason codes are emitted: no resource names, values,
addresses, filenames, variables, outputs, or provider credentials are printed.
"""
from __future__ import annotations
import argparse
import json
import re
from collections import Counter
from pathlib import Path

MAX_BYTES = 50 * 1024 * 1024
KNOWN_ACTIONS = {
    ("no-op",), ("read",), ("create",), ("update",), ("delete",),
    ("delete", "create"), ("create", "delete"), ("forget",), ("create", "forget"),
}


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON keys are unsupported")
        result[key] = value
    return result


def reject_constant(_value: str) -> None:
    raise ValueError("Non-finite JSON numbers are unsupported")


def load_plan(path: Path) -> dict:
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("Plan exceeds size limit")
    return json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant)


def actions(change: object) -> tuple[str, ...]:
    if not isinstance(change, dict):
        raise ValueError("Missing change object")
    values = change.get("actions")
    if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
        raise ValueError("Missing or unsupported actions")
    result = tuple(values)
    if result not in KNOWN_ACTIONS:
        raise ValueError("Unsupported action sequence")
    return result


def review(plan: object) -> dict:
    if not isinstance(plan, dict):
        raise ValueError("Expected a Terraform plan object")
    if not re.fullmatch(r"1\.\d+", str(plan.get("format_version", ""))):
        raise ValueError("Unsupported JSON format major version")
    # Reject state files and partial exports instead of treating absent changes as safe.
    for name in ("planned_values", "configuration"):
        if not isinstance(plan.get(name), dict):
            raise ValueError("Expected a complete plan export, not state JSON")
    for name in ("complete", "errored", "applyable"):
        if not isinstance(plan.get(name), bool):
            raise ValueError("Required plan status is absent; use a supported Terraform export")
    changes = plan.get("resource_changes")
    if not isinstance(changes, list):
        raise ValueError("Explicit resource_changes array is required by this reviewer")
    reasons: Counter = Counter()
    if not plan["complete"]:
        reasons["INCOMPLETE_PLAN"] += 1
    if plan["errored"]:
        reasons["ERRORED_PLAN"] += 1
    for key, code in (("resource_drift", "DRIFT_REQUIRES_REVIEW"),
                      ("deferred_changes", "DEFERRED_CHANGES"),
                      ("action_invocations", "ACTION_INVOCATIONS_REQUIRE_REVIEW")):
        values = plan.get(key, [])
        if not isinstance(values, list):
            raise ValueError("Unsupported change collection")
        if values:
            reasons[code] += len(values)
    for item in changes:
        if not isinstance(item, dict) or item.get("mode") not in ("managed", "data"):
            raise ValueError("Unsupported resource change")
        if not isinstance(item.get("type"), str):
            raise ValueError("Missing resource type")
        act = actions(item.get("change"))
        if "delete" in act or "forget" in act:
            reasons["DESTRUCTIVE_OR_UNMANAGED"] += 1
        if act not in (("no-op",), ("read",)):
            reasons["MUTATION_REQUIRES_REVIEW"] += 1
            if item["type"].startswith("aws_route53_"):
                reasons["DNS_CHANGE"] += 1
            if item["type"].startswith(("aws_db_", "aws_rds_", "aws_ebs_", "aws_kms_")):
                reasons["DATA_OR_KEY_CHANGE"] += 1
        if item.get("previous_address") or item["change"].get("importing") is not None:
            reasons["STATE_OWNERSHIP_CHANGE"] += 1
    outputs = plan.get("output_changes", {})
    if not isinstance(outputs, dict):
        raise ValueError("Unsupported output_changes")
    for change in outputs.values():
        if actions(change) != ("no-op",):
            reasons["OUTPUT_CHANGE_REQUIRES_REVIEW"] += 1
    checks = plan.get("checks", [])
    if not isinstance(checks, list):
        raise ValueError("Unsupported checks")
    for check in checks:
        if not isinstance(check, dict) or check.get("status") != "pass":
            reasons["CHECK_NOT_PASSED"] += 1
    return {
        "status": "REVIEW_REQUIRED" if reasons else "NO_FLAGS_IN_SUPPORTED_FIELDS",
        "resource_change_count": len(changes),
        "reason_counts": dict(sorted(reasons.items())),
        "apply_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    try:
        result = review(load_plan(args.plan))
    except (OSError, ValueError, RecursionError, UnicodeError):
        # Never echo parser errors: they can contain sensitive input or paths.
        print(json.dumps({"status": "INVALID_OR_UNSUPPORTED_INPUT", "apply_authorized": False}))
        return 2
    print(json.dumps(result, indent=2))
    return 1 if result["reason_counts"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
