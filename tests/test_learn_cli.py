from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "curriculum/modules.json").read_text(encoding="utf-8"))


class LearnCliTests(unittest.TestCase):
    def make_fixture(self, temporary: str) -> Path:
        fixture = Path(temporary) / "repo"
        shutil.copytree(ROOT / "bin", fixture / "bin")
        shutil.copytree(ROOT / "curriculum", fixture / "curriculum")
        for module in MANIFEST["modules"]:
            source = ROOT / module["folder"]
            target = fixture / module["folder"]
            target.mkdir(parents=True, exist_ok=True)
            for name in ("README.md", "lesson.md", "walkthrough.md", "checks.md"):
                shutil.copy2(source / name, target / name)
            check_file = source / "run_checks.m"
            if check_file.exists():
                shutil.copy2(check_file, target / "run_checks.m")
        return fixture

    def invoke(self, fixture: Path, *args: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [str(fixture / "bin/learn"), *args],
            cwd=fixture,
            text=True,
            capture_output=True,
            env=environment,
            timeout=10,
        )

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary:
            return self.invoke(self.make_fixture(temporary), *args)

    def test_status_and_list_derive_moving_frontier_from_manifest(self):
        implemented = sum(module["status"] == "implemented" for module in MANIFEST["modules"])
        status = self.run_cli("status")
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertIn(f"{MANIFEST['module_count']} total, {implemented} implemented", status.stdout)
        listing = self.run_cli("list")
        self.assertEqual(listing.returncode, 0, listing.stderr)
        lines = [line for line in listing.stdout.splitlines() if line.strip()]
        self.assertEqual(len(lines), MANIFEST["module_count"])
        for module, line in zip(MANIFEST["modules"], lines):
            self.assertIn(module["id"], line)
            self.assertIn(f"[{module['status']}]", line)

    def test_p01_through_p06_start_as_permanent_implemented_slices(self):
        for module_id in ("P01", "P02", "P03", "P04", "P05", "P06"):
            with self.subTest(module=module_id):
                started = self.run_cli("start", module_id)
                self.assertEqual(started.returncode, 0, started.stderr)
                self.assertIn(f"{module_id} —", started.stdout)
                self.assertIn("Status: implemented", started.stdout)
                self.assertIn("Guiding question:", started.stdout)
                self.assertNotIn("Activate its governed implementation batch", started.stdout)

    def test_p06_start_persists_and_continue_resumes_without_losing_progress(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(temporary)
            state_dir = fixture / ".learning"
            state_dir.mkdir()
            original = {
                "current": "P05",
                "completed": {"P01": True, "P05": True},
                "notes": {"P05": "retained fixed-point teach-back"},
            }
            (state_dir / "progress.json").write_text(
                json.dumps(original) + "\n",
                encoding="utf-8",
            )

            started = self.invoke(fixture, "start", "P06")
            self.assertEqual(started.returncode, 0, started.stderr)
            self.assertIn("P06 — Pipeline a Multiply-Accumulate", started.stdout)
            selected = json.loads(
                (state_dir / "progress.json").read_text(encoding="utf-8")
            )
            self.assertEqual(selected["current"], "P06")
            self.assertEqual(selected["completed"], original["completed"])
            self.assertEqual(selected["notes"], original["notes"])

            resumed = self.invoke(fixture, "continue")
            self.assertEqual(resumed.returncode, 0, resumed.stderr)
            self.assertIn("P06 — Pipeline a Multiply-Accumulate", resumed.stdout)
            self.assertEqual(
                json.loads(
                    (state_dir / "progress.json").read_text(encoding="utf-8")
                ),
                selected,
            )

    def test_p02_through_p06_checks_route_to_executable_matlab_checks(self):
        for module_id in ("P02", "P03", "P04", "P05", "P06"):
            with self.subTest(module=module_id):
                checked = self.run_cli("check", module_id)
                self.assertEqual(checked.returncode, 0, checked.stderr)
                self.assertIn(f"run_module_checks('{module_id}')", checked.stdout)

    def test_manifest_derived_scaffold_refuses_without_corrupting_resume(self):
        scaffold = next(
            (module for module in MANIFEST["modules"] if module["status"] == "scaffolded"),
            None,
        )
        if scaffold is None:
            self.skipTest("The canonical curriculum no longer contains a scaffold.")
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(temporary)
            selected = self.invoke(fixture, "start", "P02")
            self.assertEqual(selected.returncode, 0, selected.stderr)
            refused = self.invoke(fixture, "start", scaffold["id"])
            self.assertEqual(refused.returncode, 2)
            self.assertIn("Activate its governed implementation batch", refused.stdout)
            resumed = self.invoke(fixture, "continue")
            self.assertEqual(resumed.returncode, 0, resumed.stderr)
            self.assertIn("P02 — Build Combinational Logic from Truth Tables", resumed.stdout)

    def test_legacy_scaffold_state_recovers_to_nearest_implemented_prerequisite(self):
        scaffold = next(
            (module for module in MANIFEST["modules"] if module["status"] == "scaffolded"),
            None,
        )
        if scaffold is None:
            self.skipTest("The canonical curriculum no longer contains a scaffold.")
        expected = [
            module
            for module in MANIFEST["modules"]
            if module["number"] < scaffold["number"] and module["status"] == "implemented"
        ][-1]
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(temporary)
            state_dir = fixture / ".learning"
            state_dir.mkdir()
            (state_dir / "progress.json").write_text(
                json.dumps({"current": scaffold["id"], "completed": {}, "notes": {}}) + "\n",
                encoding="utf-8",
            )
            restarted = self.invoke(fixture, "start")
            self.assertEqual(restarted.returncode, 0, restarted.stderr)
            saved = json.loads((state_dir / "progress.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["current"], expected["id"])

    def test_continue_persists_legacy_scaffold_recovery_and_preserves_progress(self):
        scaffold = next(
            (module for module in MANIFEST["modules"] if module["status"] == "scaffolded"),
            None,
        )
        if scaffold is None:
            self.skipTest("The canonical curriculum no longer contains a scaffold.")
        expected = [
            module
            for module in MANIFEST["modules"]
            if module["number"] < scaffold["number"] and module["status"] == "implemented"
        ][-1]
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(temporary)
            state_dir = fixture / ".learning"
            state_dir.mkdir()
            original = {
                "current": scaffold["id"],
                "completed": {"P01": True},
                "notes": {"P01": "retained teach-back"},
            }
            (state_dir / "progress.json").write_text(
                json.dumps(original) + "\n",
                encoding="utf-8",
            )

            resumed = self.invoke(fixture, "continue")
            self.assertEqual(resumed.returncode, 0, resumed.stderr)
            self.assertIn(f"{expected['id']} —", resumed.stdout)

            saved = json.loads((state_dir / "progress.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["current"], expected["id"])
            self.assertEqual(saved["completed"], original["completed"])
            self.assertEqual(saved["notes"], original["notes"])

            status = self.invoke(fixture, "status")
            self.assertEqual(status.returncode, 0, status.stderr)
            self.assertIn(f"Current: {expected['id']}", status.stdout)

    def test_unknown_module_is_rejected(self):
        result = self.run_cli("start", "P99")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown module: P99", result.stderr)

    def test_cli_fixture_does_not_mutate_repository_learning_state(self):
        state_file = ROOT / ".learning/progress.json"
        before = state_file.read_bytes() if state_file.exists() else None
        result = self.run_cli("start", "P02")
        self.assertEqual(result.returncode, 0, result.stderr)
        after = state_file.read_bytes() if state_file.exists() else None
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
