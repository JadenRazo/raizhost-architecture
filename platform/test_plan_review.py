"""Synthetic plans only. These tests do not resolve production drift."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from plan_review import review, load_plan


def fixture(action=("no-op",), kind="aws_instance"):
    return {"format_version": "1.2", "planned_values": {}, "configuration": {},
            "complete": True, "errored": False, "applyable": True,
            "resource_changes": [{"mode": "managed", "type": kind,
                                  "change": {"actions": list(action)}}]}


class PlanReviewTests(unittest.TestCase):
    def test_noop_never_authorizes_apply(self):
        result = review(fixture())
        self.assertEqual(result["reason_counts"], {})
        self.assertFalse(result["apply_authorized"])

    def test_dns_delete_regression(self):
        reasons = review(fixture(("delete",), "aws_route53_record"))["reason_counts"]
        self.assertEqual(reasons["DNS_CHANGE"], 1)
        self.assertEqual(reasons["DESTRUCTIVE_OR_UNMANAGED"], 1)

    def test_both_replacement_orders(self):
        for action in (("delete", "create"), ("create", "delete")):
            with self.subTest(action=action):
                reasons = review(fixture(action, "aws_db_instance"))["reason_counts"]
                self.assertIn("DESTRUCTIVE_OR_UNMANAGED", reasons)
                self.assertIn("DATA_OR_KEY_CHANGE", reasons)

    def test_in_place_database_update(self):
        self.assertIn("DATA_OR_KEY_CHANGE",
                      review(fixture(("update",), "aws_ebs_volume"))["reason_counts"])

    def test_new_spend_requires_review(self):
        self.assertIn("MUTATION_REQUIRES_REVIEW",
                      review(fixture(("create",)))["reason_counts"])

    def test_read_only_data_source(self):
        plan = fixture(("read",))
        plan["resource_changes"][0]["mode"] = "data"
        self.assertEqual(review(plan)["reason_counts"], {})

    def test_forget_requires_review(self):
        self.assertIn("DESTRUCTIVE_OR_UNMANAGED",
                      review(fixture(("forget",)))["reason_counts"])

    def test_import_and_move_require_review(self):
        for key, value in (("previous_address", "old.example"), ("importing", {"id": "private"})):
            plan = fixture()
            entry = plan["resource_changes"][0]
            (entry["change"] if key == "importing" else entry)[key] = value
            self.assertIn("STATE_OWNERSHIP_CHANGE", review(plan)["reason_counts"])

    def test_status_flags_and_drift(self):
        for key, value in (("complete", False), ("errored", True),
                           ("resource_drift", [{}]), ("deferred_changes", [{}]),
                           ("action_invocations", [{}])):
            plan = fixture()
            plan[key] = value
            self.assertTrue(review(plan)["reason_counts"])

    def test_state_json_and_missing_metadata_rejected(self):
        for key in ("configuration", "planned_values", "resource_changes", "complete"):
            plan = fixture()
            del plan[key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                review(plan)

    def test_unknown_formats_actions_modes_rejected(self):
        plans = [fixture(("mystery",)), fixture(())]
        bad = fixture(); bad["format_version"] = "2.0"; plans.append(bad)
        bad = fixture(); bad["resource_changes"][0]["mode"] = "mystery"; plans.append(bad)
        for plan in plans:
            with self.assertRaises(ValueError):
                review(plan)

    def test_output_and_unknown_check_require_review(self):
        plan = fixture()
        plan["output_changes"] = {"private": {"actions": ["update"]}}
        plan["checks"] = [{"status": "unknown"}]
        self.assertEqual(len(review(plan)["reason_counts"]), 2)

    def test_values_and_addresses_are_never_emitted(self):
        plan = fixture(("delete",))
        plan["resource_changes"][0].update({"address": "SECRET_SENTINEL"})
        plan["resource_changes"][0]["change"]["before"] = {"password": "SECRET_SENTINEL"}
        self.assertNotIn("SECRET_SENTINEL", json.dumps(review(plan)))

    def test_duplicate_and_nonfinite_json_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.json"
            for text in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
                path.write_text(text)
                with self.assertRaises(ValueError):
                    load_plan(path)

    def test_cli_exit_codes_and_error_redaction(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "SECRET_SENTINEL.json"
            for text, expected in ((json.dumps(fixture()), 0),
                                   (json.dumps(fixture(("delete",))), 1),
                                   ('{"SECRET_SENTINEL":', 2)):
                path.write_text(text)
                run = subprocess.run([sys.executable, str(Path(__file__).with_name("plan_review.py")),
                                      str(path)], capture_output=True, text=True, check=False)
                self.assertEqual(run.returncode, expected)
                self.assertNotIn("SECRET_SENTINEL", run.stdout + run.stderr)
                self.assertFalse(json.loads(run.stdout)["apply_authorized"])


if __name__ == "__main__":
    unittest.main()
