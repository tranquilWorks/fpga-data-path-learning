from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_FOLDER = ROOT / "modules/03-store-state-with-registers"
GUIDING_QUESTION = (
    "What inputs, observable effects, and failure modes matter when you store "
    "State with Registers?"
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
EXPECTED_INPUT = [9, 2, 13, 5, 14, 7, 1, 12, 3, 10, 6, 15, 4, 11, 8, 1]


class P03ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "curriculum/modules.json").read_text(encoding="utf-8")
        )
        cls.module = next(module for module in cls.manifest["modules"] if module["id"] == "P03")

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
                "evidence_level": self.module["evidence_level"],
            },
            {
                "number": 3,
                "id": "P03",
                "title": "Store State with Registers",
                "guiding_question": GUIDING_QUESTION,
                "phase": 1,
                "phase_title": "Digital logic",
                "slug": "store-state-with-registers",
                "folder": "modules/03-store-state-with-registers",
                "implementation_batch": "P03",
                "prerequisites": ["P02"],
                "status": "implemented",
                "evidence_level": "simulated",
            },
        )
        p02 = next(module for module in self.manifest["modules"] if module["id"] == "P02")
        self.assertEqual(p02["status"], "implemented")
        names = {path.name for path in MODULE_FOLDER.iterdir() if path.is_file()}
        self.assertTrue(REQUIRED_ARTIFACTS <= names)
        for name in REQUIRED_ARTIFACTS:
            with self.subTest(artifact=name):
                self.assertGreater((MODULE_FOLDER / name).stat().st_size, 0)

    def test_learning_slice_is_complete_concept_first_and_prerequisite_linked(self):
        combined = "\n".join(self.read(name) for name in REQUIRED_ARTIFACTS).lower()
        for placeholder in ("scaffolded", "todo", "tbd", "implement model.m"):
            self.assertNotIn(placeholder, combined)
        for name in ("README.md", "lesson.m", "lesson.md"):
            with self.subTest(artifact=name):
                self.assertIn(GUIDING_QUESTION, self.read(name))
        lesson = self.read("lesson.md").lower()
        walkthrough = self.read("walkthrough.md").lower()
        checks = self.read("checks.md").lower()
        for marker in ("p02", "truth table", "no stored history", "pre-edge", "post-edge"):
            self.assertIn(marker, lesson)
        for marker in ("read", "baseline", "lever 1", "lever 2", "mechanism first"):
            self.assertIn(marker, lesson)
        self.assertIn("make no second prediction", lesson)
        self.assertIn("make no second prediction", walkthrough)
        self.assertIn("one prompt at a time", checks)
        self.assertIn("teach-back", checks)
        self.assertIn("two sentences", checks)
        for limitation in ("setup/hold", "metastability", "not a physical"):
            self.assertIn(limitation, lesson)

    def test_model_is_transparent_deterministic_bounded_and_presentation_free(self):
        source = self.read("model.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        for expression in (
            "cycle=(1:16).';",
            "inputData=[9213514711231061541181].';",
            "reset=cycle==1;",
            "captureEnable=reset|(cycle>=2&mod(cycle-2,enablePeriod)==0);",
            "correctNextState(stageIndex)=previousReferenceState(stageIndex-1);",
            "nextState(stageIndex)=nextState(stageIndex-1);",
            "nextState(stageIndex)=previousState(stageIndex-1);",
            "mismatchMask=outputValid~=referenceOutputValid|valueMismatch;",
        ):
            self.assertIn(expression, compact)
        for field in (
            "stateBefore",
            "stateAfter",
            "validBefore",
            "validAfter",
            "referenceStateAfter",
            "output",
            "outputValid",
            "mismatchCycles",
            "earlyValidCount",
            "captureCount",
            "holdCount",
            "firstValidCycle",
            "additionalActiveEdgeDelay",
            "dataStorageBitCount",
        ):
            self.assertIn(field, source)
        for identifier in (
            "P03:InvalidStageCount",
            "P03:InvalidEnablePeriod",
            "P03:InvalidSelectedCycle",
            "P03:InvalidBrokenCascade",
        ):
            self.assertIn(identifier, source)
        for validator in ("isnumeric", "islogical", "isreal", "isscalar", "isnan", "isinf", "fix"):
            self.assertIn(validator, lower)
        for presentation_call in ("figure", "plot", "stairs", "uifigure", "uiaxes", "disp", "fprintf"):
            self.assertIsNone(
                re.search(rf"\b{presentation_call}\s*\(", lower), presentation_call
            )
        for opaque_stateful_or_external in (
            "fi(",
            "dsp.",
            "hdl.",
            "sim(",
            "eval(",
            "system(",
            "webread",
            "fopen(",
            "rand(",
            "rng(",
            "global ",
            "persistent ",
            "timer(",
            "pause(",
            "parfeval(",
            "while ",
        ):
            self.assertNotIn(opaque_stateful_or_external, lower)

    def test_experiment_has_independent_sweeps_labels_metrics_and_broken_case(self):
        source = self.read("experiment.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        self.assertGreaterEqual(source.count("%%"), 6)
        self.assertIn("sweep 1", lower)
        self.assertIn("sweep 2", lower)
        self.assertIn("stageCounts=1:4;", compact)
        self.assertIn("enablePeriods=1:4;", compact)
        self.assertIn("model(stageCounts(sweepIndex),1,6,false)", compact)
        self.assertIn("model(1,enablePeriods(sweepIndex),6,false)", compact)
        self.assertIn("depth sweep must not change the enable schedule", lower)
        self.assertIn("enable sweep must keep register depth at one", lower)
        self.assertIn("deliberately broken case", lower)
        self.assertIn("broken=model(3,1,6,true);", compact)
        self.assertIn("all edge-triggered registers sample", lower)
        self.assertIn("broken.earlyvalidcount==2", compact.lower())
        self.assertGreaterEqual(lower.count("xlabel("), 7)
        self.assertGreaterEqual(lower.count("ylabel("), 7)
        for unit_marker in ("[cycles]", "[binary]", "[0..15]", "[edges]"):
            self.assertIn(unit_marker, lower)
        for metric in ("captured samples", "held edges", "first valid cycle", "mismatched output cycles"):
            self.assertIn(metric, lower)
        self.assertIn("~baseline.outputvalid", compact.lower())
        self.assertIn("~healthydeep.outputvalid", compact.lower())
        self.assertNotIn("close all", lower)

    def test_interactive_controls_are_bounded_model_backed_and_fault_safe(self):
        source = self.read("interactive.m")
        lower = source.lower()
        self.assertIn("modelFcn = @model", source)
        self.assertGreaterEqual(lower.count("uispinner("), 3)
        self.assertIn("uicheckbox(", lower)
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*1\s+4\s*\]")
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*1\s+16\s*\]")
        self.assertGreaterEqual(source.count("ValueChangedFcn"), 4)
        self.assertIn("faultCheckbox.Enable = 'off'", source)
        self.assertIn("faultCheckbox.Value = false", source)
        self.assertIn("plottedOutput(~out.outputValid) = NaN", source)
        self.assertIn("plottedState(~out.validAfter) = NaN", source)
        self.assertIn("Selected invalid fill", source)
        for phrase in (
            "reset has priority over enable",
            "pre-edge sampling",
            "modeled data storage",
            "mismatches",
        ):
            self.assertIn(phrase, lower)
        self.assertNotIn("close all", lower)

    def test_checks_cover_recurrence_limits_fault_validation_and_recovery(self):
        source = self.read("run_checks.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "").lower()
        self.assertGreaterEqual(lower.count("assert("), 28)
        self.assertIn("expectedinput=[9213514711231061541181].';", compact)
        self.assertIn("expectedoutput=[0213514711231061541181].';", compact)
        self.assertIn("expectedcaptures=[15854];", compact)
        self.assertIn("expectedholds=[071011];", compact)
        self.assertIn("find(brokenthree.earlyvalidmask),(2:3).'", compact)
        self.assertIn("sparsedeep=model(3,3,8,false);", compact)
        self.assertIn("sparsedeep.validafter(disableddeepedges,:)", compact)
        self.assertIn("sparsedeep.firstvalidcycle==8", compact)
        for identifier in (
            "P03:BaselineTrace",
            "P03:ResetPriority",
            "P03:HoldInvariant",
            "P03:SimultaneousTransfer",
            "P03:DeepHoldInvariant",
            "P03:EnabledEdgeLatency",
            "P03:DepthSweep",
            "P03:EnableSweep",
            "P03:BrokenCascade",
            "P03:EarlyOutput",
            "P03:ResourceBound",
            "P03:DeterminismRecovery",
            "P03:InvalidStageCount",
            "P03:InvalidEnablePeriod",
            "P03:InvalidSelectedCycle",
            "P03:InvalidBrokenCascade",
        ):
            self.assertIn(identifier.lower(), lower)
        self.assertIn("p03 checks passed", lower)

    def test_p03_text_files_have_exactly_one_terminal_newline(self):
        for name in REQUIRED_ARTIFACTS:
            with self.subTest(artifact=name):
                data = (MODULE_FOLDER / name).read_bytes()
                self.assertTrue(data.endswith(b"\n"))
                self.assertFalse(data.endswith(b"\n\n"))
                self.assertNotIn(b"\r", data)


class P03IndependentOracleTests(unittest.TestCase):
    @staticmethod
    def oracle(stage_count=1, enable_period=1, selected_cycle=6, broken_cascade=False):
        if type(stage_count) is not int or not 1 <= stage_count <= 4:
            raise ValueError("stage_count")
        if type(enable_period) is not int or not 1 <= enable_period <= 4:
            raise ValueError("enable_period")
        if type(selected_cycle) is not int or not 1 <= selected_cycle <= 16:
            raise ValueError("selected_cycle")
        valid_flag = type(broken_cascade) is bool or (
            type(broken_cascade) is int and broken_cascade in (0, 1)
        )
        if not valid_flag:
            raise ValueError("broken_cascade")
        broken_cascade = bool(broken_cascade)

        data = EXPECTED_INPUT.copy()
        reset = [cycle == 1 for cycle in range(1, 17)]
        enable = [
            is_reset or (cycle >= 2 and (cycle - 2) % enable_period == 0)
            for cycle, is_reset in zip(range(1, 17), reset)
        ]
        previous = [0] * stage_count
        previous_valid = [False] * stage_count
        previous_reference = previous.copy()
        previous_reference_valid = previous_valid.copy()
        state_before = []
        state_after = []
        valid_before = []
        valid_after = []
        reference_after = []
        reference_valid_after = []

        for index in range(16):
            state_before.append(previous.copy())
            valid_before.append(previous_valid.copy())
            next_state = previous.copy()
            next_valid = previous_valid.copy()
            correct_next = previous_reference.copy()
            correct_valid = previous_reference_valid.copy()
            if reset[index]:
                next_state = [0] * stage_count
                next_valid = [False] * stage_count
                correct_next = [0] * stage_count
                correct_valid = [False] * stage_count
            elif enable[index]:
                next_state[0] = data[index]
                next_valid[0] = True
                correct_next[0] = data[index]
                correct_valid[0] = True
                for stage in range(1, stage_count):
                    correct_next[stage] = previous_reference[stage - 1]
                    correct_valid[stage] = previous_reference_valid[stage - 1]
                    if broken_cascade:
                        next_state[stage] = next_state[stage - 1]
                        next_valid[stage] = next_valid[stage - 1]
                    else:
                        next_state[stage] = previous[stage - 1]
                        next_valid[stage] = previous_valid[stage - 1]
            state_after.append(next_state.copy())
            valid_after.append(next_valid.copy())
            reference_after.append(correct_next.copy())
            reference_valid_after.append(correct_valid.copy())
            previous = next_state
            previous_valid = next_valid
            previous_reference = correct_next
            previous_reference_valid = correct_valid

        output = [state[-1] for state in state_after]
        output_valid = [valid[-1] for valid in valid_after]
        reference_output = [state[-1] for state in reference_after]
        reference_output_valid = [valid[-1] for valid in reference_valid_after]
        mismatch = [
            actual_valid != expected_valid
            or (
                actual_valid
                and expected_valid
                and actual_value != expected_value
            )
            for actual_value, actual_valid, expected_value, expected_valid in zip(
                output, output_valid, reference_output, reference_output_valid
            )
        ]
        accepted = [enabled and not is_reset for enabled, is_reset in zip(enable, reset)]
        selected = selected_cycle - 1
        return {
            "data": data,
            "reset": reset,
            "enable": enable,
            "accepted": accepted,
            "state_before": state_before,
            "state_after": state_after,
            "valid_before": valid_before,
            "valid_after": valid_after,
            "reference_after": reference_after,
            "reference_valid_after": reference_valid_after,
            "output": output,
            "output_valid": output_valid,
            "reference_output": reference_output,
            "reference_output_valid": reference_output_valid,
            "mismatch_cycles": [index + 1 for index, value in enumerate(mismatch) if value],
            "early_valid_cycles": [
                index + 1
                for index, (actual, expected) in enumerate(
                    zip(output_valid, reference_output_valid)
                )
                if actual and not expected
            ],
            "capture_count": sum(accepted),
            "hold_count": sum(
                not is_reset and not enabled for is_reset, enabled in zip(reset, enable)
            ),
            "first_valid_cycle": output_valid.index(True) + 1,
            "additional_delay": stage_count - 1,
            "data_storage_bits": 4 * stage_count,
            "selected_before": state_before[selected],
            "selected_after": state_after[selected],
        }

    def test_exact_baseline_reset_capture_and_validity(self):
        result = self.oracle()
        self.assertEqual(result["data"], EXPECTED_INPUT)
        self.assertEqual(result["output"], [0] + EXPECTED_INPUT[1:])
        self.assertEqual(result["output_valid"], [False] + [True] * 15)
        self.assertTrue(result["reset"][0])
        self.assertTrue(result["enable"][0])
        self.assertEqual(result["capture_count"], 15)
        self.assertEqual(result["hold_count"], 0)
        self.assertEqual(result["selected_before"], [14])
        self.assertEqual(result["selected_after"], [7])

    def test_depth_sweep_delay_validity_storage_and_isolation(self):
        results = [self.oracle(stage_count=stage) for stage in range(1, 5)]
        self.assertEqual([result["first_valid_cycle"] for result in results], [2, 3, 4, 5])
        self.assertEqual([result["additional_delay"] for result in results], [0, 1, 2, 3])
        self.assertEqual([result["data_storage_bits"] for result in results], [4, 8, 12, 16])
        self.assertEqual([result["capture_count"] for result in results], [15] * 4)
        for stage, result in enumerate(results, start=1):
            with self.subTest(stage=stage):
                self.assertEqual(result["enable"], results[0]["enable"])
                self.assertEqual(result["data"], EXPECTED_INPUT)
                self.assertEqual(result["output"], [0] * stage + EXPECTED_INPUT[1 : 17 - stage])
                self.assertEqual(result["output_valid"], [False] * stage + [True] * (16 - stage))

    def test_enable_sweep_capture_hold_trace_and_isolation(self):
        results = [self.oracle(enable_period=period) for period in range(1, 5)]
        self.assertEqual([result["capture_count"] for result in results], [15, 8, 5, 4])
        self.assertEqual([result["hold_count"] for result in results], [0, 7, 10, 11])
        self.assertEqual(
            results[3]["output"],
            [0, 2, 2, 2, 2, 7, 7, 7, 7, 10, 10, 10, 10, 11, 11, 11],
        )
        for result in results:
            self.assertEqual(len(result["state_after"][0]), 1)
            self.assertEqual(result["data"], EXPECTED_INPUT)
            for index in range(1, 16):
                if not result["enable"][index]:
                    self.assertEqual(result["state_after"][index], result["state_before"][index])

    def test_pre_edge_recurrence_reset_capture_and_hold_partition(self):
        for stage_count in range(1, 5):
            for enable_period in range(1, 5):
                result = self.oracle(stage_count, enable_period)
                with self.subTest(stage_count=stage_count, enable_period=enable_period):
                    for index in range(16):
                        if index:
                            self.assertEqual(result["state_before"][index], result["state_after"][index - 1])
                        if result["reset"][index]:
                            self.assertEqual(result["state_after"][index], [0] * stage_count)
                            self.assertEqual(result["valid_after"][index], [False] * stage_count)
                        elif result["enable"][index]:
                            self.assertEqual(result["state_after"][index][0], EXPECTED_INPUT[index])
                            self.assertEqual(
                                result["state_after"][index][1:], result["state_before"][index][:-1]
                            )
                        else:
                            self.assertEqual(result["state_after"][index], result["state_before"][index])
                    self.assertEqual(result["capture_count"] + result["hold_count"] + 1, 16)

    def test_sparse_enable_stalls_every_stage_and_validity_bit(self):
        result = self.oracle(stage_count=3, enable_period=3, selected_cycle=8)
        disabled_edges = [
            index
            for index, (is_reset, enabled) in enumerate(
                zip(result["reset"], result["enable"])
            )
            if not is_reset and not enabled
        ]
        for index in disabled_edges:
            with self.subTest(cycle=index + 1):
                self.assertEqual(result["state_after"][index], result["state_before"][index])
                self.assertEqual(result["valid_after"][index], result["valid_before"][index])
        self.assertEqual(result["first_valid_cycle"], 8)
        self.assertEqual(result["output_valid"], [False] * 7 + [True] * 9)
        self.assertEqual(result["selected_before"], [14, 2, 0])
        self.assertEqual(result["selected_after"], [12, 14, 2])
        self.assertEqual(result["output"][7], 2)

    def test_broken_cascade_symptom_reference_and_single_stage_limit(self):
        healthy = self.oracle(3, 1, 6, False)
        broken = self.oracle(3, 1, 6, True)
        self.assertEqual(healthy["state_after"][3], [5, 13, 2])
        self.assertEqual(broken["state_after"][3], [5, 5, 5])
        self.assertEqual(broken["mismatch_cycles"], list(range(2, 17)))
        self.assertEqual(broken["early_valid_cycles"], [2, 3])
        self.assertEqual(broken["reference_output"], healthy["output"])
        self.assertEqual(broken["reference_output_valid"], healthy["output_valid"])
        single = self.oracle(1, 1, 6, True)
        self.assertEqual(single["mismatch_cycles"], [])
        self.assertEqual(single["early_valid_cycles"], [])

    def test_malformed_inputs_reject_and_valid_call_recovers(self):
        invalid_calls = (
            (0, 1, 6, False),
            (5, 1, 6, False),
            (2.5, 1, 6, False),
            ([1, 2], 1, 6, False),
            (1, 0, 6, False),
            (1, 5, 6, False),
            (1, 2.5, 6, False),
            (1, [1, 2], 6, False),
            (1, math.nan, 6, False),
            (1, math.inf, 6, False),
            (1, 1 + 0j, 6, False),
            (1, 1, 0, False),
            (1, 1, 17, False),
            (1, 1, 2.5, False),
            (1, 1, [1, 2], False),
            (1, 1, math.nan, False),
            (1, 1, math.inf, False),
            (1, 1, 1 + 0j, False),
            (1, 1, 6, 2),
            (1, 1, 6, math.nan),
            (1, 1, 6, 1 + 0j),
            (1, 1, 6, [False, True]),
            (1 + 0j, 1, 6, False),
        )
        expected = self.oracle()
        for arguments in invalid_calls:
            with self.subTest(arguments=arguments):
                with self.assertRaises(ValueError):
                    self.oracle(*arguments)
                self.assertEqual(self.oracle(), expected)

    def test_determinism_call_isolation_and_fixed_resource_bound(self):
        baseline = self.oracle(2, 3, 11, False)
        for stage_count in range(1, 5):
            for enable_period in range(1, 5):
                current = self.oracle(stage_count, enable_period, 16, False)
                self.assertEqual(len(current["state_after"]), 16)
                self.assertTrue(all(len(row) == stage_count for row in current["state_after"]))
                self.assertLessEqual(sum(len(row) for row in current["state_after"]), 64)
                self.assertTrue(
                    all(
                        isinstance(value, int) and 0 <= value <= 15
                        for row in current["state_after"]
                        for value in row
                    )
                )
                self.assertEqual(current["mismatch_cycles"], [])
        self.oracle(4, 4, 16, True)
        self.assertEqual(self.oracle(2, 3, 11, False), baseline)


if __name__ == "__main__":
    unittest.main()
