"""An unrelated or weaker passing check must not hide omitted task gates."""

import copy
from test_workbench import Project
from ror2_workbench.core import json_bytes, read_json


class CoverageTests(Project):
    def save(self, result):
        (self.root / "local/result.json").write_bytes(json_bytes(result))
        return self.cli("record", "local/result.json", "--receipt", "evidence/coverage.json")

    def test_unrelated_pass_reports_all_required_gates_missing(self):
        result = self.operator_result()
        code, output = self.save(result)
        self.assertEqual(code, 0)  # All supplied checks passed; gate coverage is separate.
        coverage = output["acceptance_coverage"]
        self.assertFalse(coverage["all_required_reported_passed"])
        self.assertEqual(coverage["missing"], ["build", "native-held-repress", "controller", "client-host"])
        self.assertEqual(coverage["unrelated_ids"], ["semantic"])
        self.assertEqual(read_json(self.root / "evidence/coverage.json")["acceptance_coverage"], coverage)

    def test_offline_check_named_like_multiplayer_does_not_cover_it(self):
        result = self.operator_result()
        result["checks"][0]["id"] = "client-host"
        code, output = self.save(result)
        self.assertEqual(code, 0)
        coverage = output["acceptance_coverage"]
        self.assertEqual(coverage["matched_passed"], [])
        self.assertEqual(coverage["level_mismatches"], [{"id":"client-host", "expected":"multiplayer", "reported":"offline"}])
        self.assertFalse(coverage["all_required_reported_passed"])

    def test_complete_attested_coverage_leaves_task_and_levels_unchanged(self):
        result = self.operator_result()
        before = (self.root / "local/task.json").read_bytes()
        task = read_json(self.root / "local/task.json")
        template = result["checks"][0]
        result["checks"] = [dict(copy.deepcopy(template), id=gate["id"], level=gate["level"]) for gate in task["acceptance"]]
        code, output = self.save(result)
        self.assertEqual(code, 0)
        self.assertTrue(output["acceptance_coverage"]["all_required_reported_passed"])
        self.assertEqual((self.root / "local/task.json").read_bytes(), before)
        receipt = read_json(self.root / "evidence/coverage.json")
        self.assertEqual(receipt["checks"], [dict(check, log_sha256=receipt["checks"][0]["log_sha256"]) for check in result["checks"]])
        self.assertEqual(receipt["runtime_compatibility"], "unverified")

    def test_failed_gate_is_preserved_and_does_not_count_as_coverage(self):
        result = self.operator_result()
        result["checks"][0].update(id="build", level="build", status="failed", exit_code=1)
        code, output = self.save(result)
        self.assertEqual(code, 1)
        self.assertEqual(output["acceptance_coverage"]["not_passed"], ["build"])
        self.assertFalse(output["acceptance_coverage"]["all_required_reported_passed"])

    def test_changed_task_gate_invalidates_previous_identity(self):
        result = self.operator_result()
        task = read_json(self.root / "local/task.json")
        task["acceptance"].append({"id":"cleanup", "level":"solo", "status":"pending", "evidence":None})
        (self.root / "local/task.json").write_bytes(json_bytes(task))
        code, output = self.save(result)
        self.assertEqual(code, 2)
        self.assertNotIn("acceptance_coverage", output)
        self.assertFalse((self.root / "evidence/coverage.json").exists())

    def test_duplicate_gate_ids_cannot_collapse_coverage(self):
        result = self.operator_result()
        task = read_json(self.root / "local/task.json")
        task["acceptance"][1]["id"] = task["acceptance"][0]["id"]
        (self.root / "local/task.json").write_bytes(json_bytes(task))
        code, output = self.save(result)
        self.assertEqual(code, 2)
        self.assertEqual(output["error"], "duplicate acceptance id")
        self.assertFalse((self.root / "evidence/coverage.json").exists())
