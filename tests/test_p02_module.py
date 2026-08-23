from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_FOLDER = ROOT / "modules/02-build-combinational-logic-from-truth-tables"
GUIDING_QUESTION = (
    "What inputs, observable effects, and failure modes matter when you build "
    "Combinational Logic from Truth Tables?"
)
REQUIRED_ARTIFACTS = {
    "README.md",
    "lesson.m",
    "model.m",
    "experiment.m",
    "interactive.m",
    "lesson.md",
    "walkthrough.md",
    "checks.md",
    "run_checks.m",
}


class P02ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "curriculum/modules.json").read_text(encoding="utf-8")
        )
        cls.module = next(module for module in cls.manifest["modules"] if module["id"] == "P02")

    def read(self, name: str) -> str:
        return (MODULE_FOLDER / name).read_text(encoding="utf-8")

    def test_permanent_manifest_identity_and_artifact_set(self):
        self.assertEqual(
            {
                "number": self.module["number"],
                "id": self.module["id"],
                "title": self.module["title"],
                "guiding_question": self.module["guiding_question"],
                "phase": self.module["phase"],
                "phase_title": self.module["phase_title"],
                "slug": self.module["slug"],
                "folder": self.module["folder"],
                "implementation_batch": self.module["implementation_batch"],
                "prerequisites": self.module["prerequisites"],
                "status": self.module["status"],
            },
            {
                "number": 2,
                "id": "P02",
                "title": "Build Combinational Logic from Truth Tables",
                "guiding_question": GUIDING_QUESTION,
                "phase": 1,
                "phase_title": "Digital logic",
                "slug": "build-combinational-logic-from-truth-tables",
                "folder": "modules/02-build-combinational-logic-from-truth-tables",
                "implementation_batch": "P02",
                "prerequisites": ["P01"],
                "status": "implemented",
            },
        )
        self.assertIn(
            self.module["evidence_level"],
            {"static", "simulated", "matlab-runtime", "bench", "hil", "field"},
        )
        p01 = next(module for module in self.manifest["modules"] if module["id"] == "P01")
        self.assertEqual(p01["status"], "implemented")
        names = {path.name for path in MODULE_FOLDER.iterdir() if path.is_file()}
        self.assertTrue(REQUIRED_ARTIFACTS <= names)
        for name in REQUIRED_ARTIFACTS:
            with self.subTest(artifact=name):
                self.assertGreater((MODULE_FOLDER / name).stat().st_size, 0)

    def test_learning_slice_is_complete_and_concept_first(self):
        combined = "\n".join(self.read(name) for name in REQUIRED_ARTIFACTS).lower()
        for placeholder in ("scaffolded", "todo", "tbd", "implement model.m"):
            self.assertNotIn(placeholder, combined)
        for name in ("README.md", "lesson.m", "lesson.md"):
            with self.subTest(artifact=name):
                self.assertIn(GUIDING_QUESTION, self.read(name))
        lesson = self.read("lesson.md").lower()
        walkthrough = self.read("walkthrough.md").lower()
        checks = self.read("checks.md").lower()
        self.assertIn("p01", lesson)
        self.assertIn("fifo", lesson)
        self.assertIn("no stored history", lesson)
        for marker in ("read", "baseline", "lever 1", "lever 2", "mechanism"):
            self.assertIn(marker, lesson)
        self.assertIn("no second prediction", walkthrough)
        self.assertIn("one prompt at a time", checks)
        self.assertIn("teach-back", checks)
        self.assertIn("two sentences", checks)
        self.assertIn("propagation delay", lesson)

    def test_model_is_transparent_deterministic_and_presentation_free(self):
        source = self.read("model.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        self.assertIn("inputAddress=(0:7).'", compact)
        self.assertIn("bitget(inputAddress,3)", compact)
        self.assertIn("bitget(inputAddress,2)", compact)
        self.assertIn("bitget(inputAddress,1)", compact)
        self.assertIn("specifiedOutput=highCount>=requiredHigh;", compact)
        self.assertIn("(A&B)|(A&C)|(B&C)", compact)
        self.assertIn(
            "lutOutput(faultAddress+1)=~lutOutput(faultAddress+1);", compact
        )
        self.assertIn(
            "rowProbability=(p.^highCount).*((1-p).^(3-highCount));", compact
        )
        self.assertIn(
            "'specifiedHighProbability',sum(rowProbability(specifiedOutput))", compact
        )
        for field in (
            "specifiedOutput",
            "lutOutput",
            "equationOutput",
            "rowProbability",
            "mismatchAddresses",
            "mismatchCount",
            "assertedRowCount",
            "specifiedHighProbability",
            "mismatchProbability",
            "truthTable",
        ):
            self.assertIn(field, source)
        for identifier in (
            "P02:InvalidRequiredHigh",
            "P02:InvalidInputHighProbability",
            "P02:InvalidSelectedAddress",
            "P02:InvalidFaultAddress",
        ):
            self.assertIn(identifier, source)
        for validator in ("isnumeric", "isreal", "isscalar", "isnan", "isinf", "fix"):
            self.assertIn(validator, lower)
        for presentation_call in ("figure", "plot", "stairs", "uifigure", "uiaxes", "disp", "fprintf"):
            self.assertIsNone(
                re.search(rf"\b{presentation_call}\s*\(", lower), presentation_call
            )
        for opaque_or_stateful in (
            "de2bi",
            "bi2de",
            "syms",
            "simplify",
            "booleanfunction",
            "eval(",
            "system(",
            "webread",
            "fopen(",
            "rand(",
            "rng(",
            "global ",
            "persistent ",
        ):
            self.assertNotIn(opaque_or_stateful, lower)

    def test_experiment_has_two_independent_sweeps_and_broken_case(self):
        source = self.read("experiment.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        self.assertGreaterEqual(source.count("%%"), 6)
        self.assertIn("sweep 1", lower)
        self.assertIn("sweep 2", lower)
        self.assertIn("thresholds=1:3;", compact)
        self.assertIn("probabilities=0:0.05:1;", compact)
        self.assertIn("model(thresholds(sweepIndex),0.5,3,-1)", compact)
        self.assertIn("model(2,probabilities(sweepIndex),3,-1)", compact)
        self.assertIn("probability sweep must not change the truth-table mapping", lower)
        self.assertIn("deliberately broken case", lower)
        self.assertIn("faultaddress = 6", lower)
        self.assertIn("every reachable lut entry matches", lower)
        self.assertGreaterEqual(lower.count("xlabel("), 4)
        self.assertGreaterEqual(lower.count("ylabel("), 4)
        for unit_marker in ("[unitless]", "[binary]", "p(y=1)"):
            self.assertIn(unit_marker, lower)
        for metric in ("asserted rows", "mismatch", "weighted error probability"):
            self.assertIn(metric, lower)
        self.assertNotIn("close all", lower)

    def test_interactive_controls_are_bounded_and_model_backed(self):
        source = self.read("interactive.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        self.assertIn("modelFcn = @model", source)
        self.assertGreaterEqual(lower.count("uispinner("), 2)
        self.assertIn("uislider(", lower)
        self.assertIn("uicheckbox(", lower)
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*1\s+3\s*\]")
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*0\s+1\s*\]")
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*0\s+7\s*\]")
        self.assertIn("0:0.02:1", compact)
        self.assertIn("ValueChangingFcn", source)
        self.assertGreaterEqual(source.count("ValueChangedFcn"), 4)
        self.assertIn("every lut entry matches its specified row", lower)
        self.assertIn("independent-input assumption", lower)
        self.assertNotIn("close all", lower)

    def test_checks_cover_limits_fault_validation_and_recovery(self):
        source = self.read("run_checks.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "").lower()
        self.assertGreaterEqual(lower.count("assert("), 18)
        self.assertIn("[00010111]", compact)
        self.assertIn("[741]", compact)
        self.assertIn("3*p^2-2*p^3", compact)
        self.assertIn("faultprobability^2*(1-faultprobability)", compact)
        for identifier in (
            "P02:BaselineVector",
            "P02:AddressOrder",
            "P02:ResourceBound",
            "P02:ThresholdSweep",
            "P02:ProbabilityEquation",
            "P02:BrokenIsolation",
            "P02:DeterminismRecovery",
            "P02:InvalidRequiredHigh",
            "P02:InvalidInputHighProbability",
            "P02:InvalidSelectedAddress",
            "P02:InvalidFaultAddress",
        ):
            self.assertIn(identifier.lower(), lower)
        self.assertIn("p02 checks passed", lower)

    def test_p02_text_files_have_exactly_one_terminal_newline(self):
        for name in REQUIRED_ARTIFACTS:
            with self.subTest(artifact=name):
                data = (MODULE_FOLDER / name).read_bytes()
                self.assertTrue(data.endswith(b"\n"))
                self.assertFalse(data.endswith(b"\n\n"))


class P02IndependentOracleTests(unittest.TestCase):
    @staticmethod
    def oracle(required_high: int, p: float, selected: int, fault: int = -1):
        if type(required_high) is not int or not 1 <= required_high <= 3:
            raise ValueError("required_high")
        if not isinstance(p, (int, float)) or isinstance(p, bool) or not math.isfinite(p) or not 0 <= p <= 1:
            raise ValueError("p")
        if type(selected) is not int or not 0 <= selected <= 7:
            raise ValueError("selected")
        if type(fault) is not int or not -1 <= fault <= 7:
            raise ValueError("fault")
        rows = [((address >> 2) & 1, (address >> 1) & 1, address & 1) for address in range(8)]
        specified = [sum(bits) >= required_high for bits in rows]
        if required_high == 1:
            equation = [bool(a or b or c) for a, b, c in rows]
        elif required_high == 2:
            equation = [bool((a and b) or (a and c) or (b and c)) for a, b, c in rows]
        else:
            equation = [bool(a and b and c) for a, b, c in rows]
        lut = specified.copy()
        if fault >= 0:
            lut[fault] = not lut[fault]
        weights = [(p ** sum(bits)) * ((1 - p) ** (3 - sum(bits))) for bits in rows]
        mismatches = [address for address in range(8) if specified[address] != lut[address]]
        return {
            "rows": rows,
            "specified": specified,
            "equation": equation,
            "lut": lut,
            "weights": weights,
            "specified_probability": sum(weight for weight, value in zip(weights, specified) if value),
            "mismatch_probability": sum(weights[address] for address in mismatches),
            "mismatches": mismatches,
            "selected_bits": rows[selected],
            "selected_output": lut[selected],
        }

    def test_exact_exhaustive_baseline_and_bit_order(self):
        result = self.oracle(2, 0.5, 3)
        self.assertEqual(result["rows"][0], (0, 0, 0))
        self.assertEqual(result["rows"][3], (0, 1, 1))
        self.assertEqual(result["rows"][7], (1, 1, 1))
        self.assertEqual(result["specified"], [False, False, False, True, False, True, True, True])
        self.assertEqual(result["specified"], result["equation"])
        self.assertEqual(result["specified"], result["lut"])
        self.assertEqual(result["selected_bits"], (0, 1, 1))
        self.assertTrue(result["selected_output"])

    def test_threshold_sweep_and_limiting_cases(self):
        outputs = [self.oracle(k, 0.5, 0)["specified"] for k in (1, 2, 3)]
        self.assertEqual([sum(values) for values in outputs], [7, 4, 1])
        self.assertEqual(outputs[0], [False, True, True, True, True, True, True, True])
        self.assertEqual(outputs[2], [False, False, False, False, False, False, False, True])

    def test_probability_sweep_matches_independent_polynomial(self):
        baseline_mapping = self.oracle(2, 0.5, 0)["specified"]
        for step in range(21):
            p = step / 20
            with self.subTest(p=p):
                result = self.oracle(2, p, 0)
                self.assertAlmostEqual(sum(result["weights"]), 1.0, places=14)
                self.assertAlmostEqual(result["specified_probability"], 3 * p**2 - 2 * p**3, places=14)
                self.assertEqual(result["specified"], baseline_mapping)

    def test_complement_symmetry_and_probability_limits(self):
        result = self.oracle(2, 0.5, 0)
        self.assertEqual(list(reversed(result["specified"])), [not value for value in result["specified"]])
        self.assertEqual(self.oracle(2, 0, 0)["specified_probability"], 0)
        self.assertEqual(self.oracle(2, 1, 0)["specified_probability"], 1)

    def test_broken_row_is_exactly_isolated(self):
        for step in range(11):
            p = step / 10
            with self.subTest(p=p):
                broken = self.oracle(2, p, 6, 6)
                self.assertEqual(broken["mismatches"], [6])
                self.assertTrue(broken["specified"][6])
                self.assertFalse(broken["lut"][6])
                self.assertAlmostEqual(broken["mismatch_probability"], p**2 * (1 - p), places=14)

    def test_malformed_inputs_reject_and_valid_call_recovers(self):
        invalid_calls = (
            (0, 0.5, 3, -1),
            (2.5, 0.5, 3, -1),
            (2, float("nan"), 3, -1),
            (2, 1.1, 3, -1),
            (2, 0.5, -1, -1),
            (2, 0.5, 3, 8),
        )
        expected = self.oracle(2, 0.5, 3)
        for arguments in invalid_calls:
            with self.subTest(arguments=arguments):
                with self.assertRaises(ValueError):
                    self.oracle(*arguments)
        self.assertEqual(self.oracle(2, 0.5, 3), expected)

    def test_determinism_isolation_and_fixed_resource_bound(self):
        first = self.oracle(2, 0.37, 5)
        for required_high in (1, 2, 3):
            for selected in range(8):
                current = self.oracle(required_high, 0.61, selected)
                self.assertEqual(len(current["rows"]), 8)
                self.assertEqual(len(set(current["rows"])), 8)
        self.oracle(1, 0.9, 7, 0)
        self.assertEqual(self.oracle(2, 0.37, 5), first)


if __name__ == "__main__":
    unittest.main()
