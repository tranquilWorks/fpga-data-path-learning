from __future__ import annotations

import json
import math
import numbers
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "modules/12-size-a-fifo-from-burst-and-service-rates"
QUESTION = (
    "What inputs, observable effects, and failure modes matter when you size "
    "a FIFO from Burst and Service Rates?"
)
ARTIFACTS = (
    "README.md",
    "checks.md",
    "experiment.m",
    "interactive.m",
    "lesson.m",
    "lesson.md",
    "model.m",
    "run_checks.m",
    "walkthrough.md",
)


def _integer_scalar(value, minimum: int, maximum: int, label: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, numbers.Real)
        or not math.isfinite(float(value))
        or float(value) != int(value)
        or int(value) < minimum
        or int(value) > maximum
    ):
        raise ValueError(label)
    return int(value)


def _boolean_scalar(value) -> bool:
    if isinstance(value, bool):
        return value
    if (
        isinstance(value, numbers.Real)
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and float(value) in (0.0, 1.0)
    ):
        return bool(value)
    raise ValueError("broken")


def simulate_oracle(
    burst_cycles=8,
    arrival_rate=3,
    service_rate=1,
    configured_depth=17,
    broken=False,
):
    """Independent registered-FIFO recurrence used as retained simulation."""
    burst_cycles = _integer_scalar(burst_cycles, 1, 8, "burst")
    arrival_rate = _integer_scalar(arrival_rate, 1, 4, "arrival")
    service_rate = _integer_scalar(service_rate, 0, 4, "service")
    configured_depth = _integer_scalar(configured_depth, 0, 32, "depth")
    broken = _boolean_scalar(broken)
    trace_cycles = 40
    arrivals = [arrival_rate if cycle < burst_cycles else 0 for cycle in range(trace_cycles)]
    service = [service_rate] * trace_cycles

    reference_before = []
    reference_after = []
    reference_departed = []
    queue = 0
    for arrival, capacity in zip(arrivals, service):
        reference_before.append(queue)
        departed = min(capacity, queue)
        reference_departed.append(departed)
        queue = queue - departed + arrival
        reference_after.append(queue)

    required_depth = max(reference_after)
    analytic_depth = arrival_rate + (burst_cycles - 1) * max(
        arrival_rate - service_rate, 0
    )
    fall_through_depth = burst_cycles * max(arrival_rate - service_rate, 0)
    applied_depth = fall_through_depth if broken else configured_depth

    applied_before = []
    applied_after = []
    applied_departed = []
    admitted = []
    not_accepted = []
    replacement = []
    queue = 0
    for arrival, capacity in zip(arrivals, service):
        applied_before.append(queue)
        departed = min(capacity, queue)
        stored = queue - departed
        free = applied_depth - stored
        accepted = min(arrival, free)
        refused = arrival - accepted
        queue = stored + accepted
        applied_departed.append(departed)
        admitted.append(accepted)
        not_accepted.append(refused)
        replacement.append(min(departed, accepted))
        applied_after.append(queue)

    total_offered = sum(arrivals)
    reference_cumulative_departed = []
    running = 0
    for value in reference_departed:
        running += value
        reference_cumulative_departed.append(running)
    if reference_after[-1] == 0 and sum(reference_departed) == total_offered:
        reference_completion = next(
            index + 1
            for index, value in enumerate(reference_cumulative_departed)
            if value == total_offered
        )
    else:
        reference_completion = None

    applied_cumulative_departed = []
    running = 0
    for value in applied_departed:
        running += value
        applied_cumulative_departed.append(running)
    total_admitted = sum(admitted)
    if applied_after[-1] == 0 and total_admitted > 0:
        admitted_completion = next(
            index + 1
            for index, value in enumerate(applied_cumulative_departed)
            if value == total_admitted
        )
    else:
        admitted_completion = None

    return {
        "burst_cycles": burst_cycles,
        "arrival_rate": arrival_rate,
        "service_rate": service_rate,
        "configured_depth": configured_depth,
        "broken": broken,
        "arrivals": arrivals,
        "service": service,
        "reference_before": reference_before,
        "reference_after": reference_after,
        "reference_departed": reference_departed,
        "required_depth": required_depth,
        "analytic_depth": analytic_depth,
        "fall_through_depth": fall_through_depth,
        "applied_depth": applied_depth,
        "applied_before": applied_before,
        "applied_after": applied_after,
        "applied_departed": applied_departed,
        "admitted": admitted,
        "not_accepted": not_accepted,
        "replacement": replacement,
        "offered_count": total_offered,
        "admitted_count": total_admitted,
        "departed_count": sum(applied_departed),
        "not_accepted_count": sum(not_accepted),
        "reference_completion": reference_completion,
        "admitted_completion": admitted_completion,
        "reference_timed_out": reference_completion is None,
        "applied_timed_out": applied_after[-1] != 0,
        "fault_active": broken and fall_through_depth < required_depth,
        "fault_visible": broken and any(not_accepted),
    }


class P12IndependentOracleTests(unittest.TestCase):
    def test_exact_registered_baseline(self):
        out = simulate_oracle()
        expected_occupancy = [
            3,
            5,
            7,
            9,
            11,
            13,
            15,
            17,
            16,
            15,
            14,
            13,
            12,
            11,
            10,
            9,
            8,
            7,
            6,
            5,
            4,
            3,
            2,
            1,
            0,
        ] + [0] * 15
        self.assertEqual(out["arrivals"], [3] * 8 + [0] * 32)
        self.assertEqual(out["reference_departed"], [0] + [1] * 24 + [0] * 15)
        self.assertEqual(out["reference_after"], expected_occupancy)
        self.assertEqual(out["required_depth"], 17)
        self.assertEqual(out["analytic_depth"], 17)
        self.assertEqual(out["offered_count"], 24)
        self.assertEqual(out["not_accepted_count"], 0)
        self.assertEqual(out["reference_completion"], 25)
        self.assertEqual(out["admitted_completion"], 25)

    def test_edge_and_final_conservation_are_independent_invariants(self):
        out = simulate_oracle()
        for before, departed, arrival, after in zip(
            out["reference_before"],
            out["reference_departed"],
            out["arrivals"],
            out["reference_after"],
        ):
            self.assertLessEqual(departed, before)
            self.assertEqual(after, before - departed + arrival)
        for before, departed, admitted, refused, offered, after in zip(
            out["applied_before"],
            out["applied_departed"],
            out["admitted"],
            out["not_accepted"],
            out["arrivals"],
            out["applied_after"],
        ):
            self.assertEqual(offered, admitted + refused)
            self.assertEqual(after, before - departed + admitted)
            self.assertLessEqual(after, out["applied_depth"])
        self.assertEqual(
            out["offered_count"],
            out["departed_count"] + out["applied_after"][-1],
        )

    def test_two_sweeps_are_exact_and_isolated(self):
        burst_cases = [simulate_oracle(burst, 3, 1, 32, False) for burst in [1, 2, 4, 6, 8]]
        self.assertEqual([case["required_depth"] for case in burst_cases], [3, 5, 9, 13, 17])
        self.assertEqual([case["offered_count"] for case in burst_cases], [3, 6, 12, 18, 24])
        self.assertEqual([case["reference_completion"] for case in burst_cases], [4, 7, 13, 19, 25])
        for case in burst_cases:
            self.assertEqual(case["arrival_rate"], 3)
            self.assertEqual(case["service_rate"], 1)
            self.assertEqual(case["configured_depth"], 32)
            self.assertFalse(case["broken"])

        service_cases = [simulate_oracle(8, 3, service, 32, False) for service in range(5)]
        self.assertEqual([case["required_depth"] for case in service_cases], [24, 17, 10, 3, 3])
        self.assertEqual(
            [case["reference_completion"] for case in service_cases],
            [None, 25, 13, 9, 9],
        )
        for service, case in enumerate(service_cases):
            self.assertEqual(case["burst_cycles"], 8)
            self.assertEqual(case["arrival_rate"], 3)
            self.assertEqual(case["configured_depth"], 32)
            self.assertEqual(case["service_rate"], service)
            self.assertFalse(case["broken"])

    def test_exact_depth_one_short_and_broken_estimate(self):
        baseline = simulate_oracle()
        one_short = simulate_oracle(8, 3, 1, 16, False)
        broken = simulate_oracle(8, 3, 1, 17, True)
        self.assertEqual(one_short["not_accepted_count"], 1)
        self.assertEqual([index + 1 for index, value in enumerate(one_short["not_accepted"]) if value], [8])
        self.assertEqual(one_short["admitted_count"], 23)
        self.assertEqual(one_short["departed_count"], 23)
        self.assertEqual(one_short["admitted_completion"], 24)
        self.assertFalse(one_short["fault_active"])
        self.assertFalse(one_short["fault_visible"])
        self.assertEqual(broken["fall_through_depth"], 16)
        self.assertEqual(broken["applied_depth"], 16)
        self.assertEqual(broken["reference_after"], baseline["reference_after"])
        self.assertEqual(broken["not_accepted"], one_short["not_accepted"])
        self.assertTrue(broken["fault_active"])
        self.assertTrue(broken["fault_visible"])

    def test_zero_depth_registered_fifo_refuses_every_offered_word(self):
        out = simulate_oracle(8, 3, 1, 0, False)
        self.assertEqual(out["applied_depth"], 0)
        self.assertEqual(out["applied_before"], [0] * 40)
        self.assertEqual(out["applied_after"], [0] * 40)
        self.assertEqual(out["admitted"], [0] * 40)
        self.assertEqual(out["applied_departed"], [0] * 40)
        self.assertEqual(out["not_accepted"], out["arrivals"])
        self.assertEqual(out["offered_count"], 24)
        self.assertEqual(out["admitted_count"], 0)
        self.assertEqual(out["departed_count"], 0)
        self.assertEqual(out["not_accepted_count"], 24)
        self.assertIsNone(out["admitted_completion"])
        self.assertFalse(out["applied_timed_out"])
        self.assertFalse(out["fault_active"])
        self.assertFalse(out["fault_visible"])

    def test_zero_service_registered_staging_and_replacement_limits(self):
        no_service = simulate_oracle(8, 3, 0, 24, False)
        self.assertEqual(no_service["required_depth"], 24)
        self.assertEqual(no_service["reference_after"][:8], list(range(3, 25, 3)))
        self.assertEqual(no_service["reference_after"][8:], [24] * 32)
        self.assertEqual(no_service["departed_count"], 0)
        self.assertTrue(no_service["reference_timed_out"])
        self.assertTrue(no_service["applied_timed_out"])
        self.assertEqual(no_service["not_accepted_count"], 0)

        matched = simulate_oracle(8, 3, 3, 3, False)
        faster = simulate_oracle(8, 3, 4, 3, False)
        self.assertEqual(matched["required_depth"], 3)
        self.assertEqual(faster["required_depth"], 3)
        self.assertEqual(matched["reference_after"][:8], [3] * 8)
        self.assertEqual(faster["reference_after"][:8], [3] * 8)
        self.assertEqual(sum(matched["replacement"][1:8]), 21)
        self.assertEqual(matched["reference_completion"], 9)
        self.assertEqual(faster["reference_completion"], 9)

    def test_complete_grid_is_deterministic_bounded_and_reference_isolated(self):
        for burst in range(1, 9):
            for arrival in range(1, 5):
                for service in range(5):
                    expected_depth = arrival + (burst - 1) * max(arrival - service, 0)
                    healthy = simulate_oracle(burst, arrival, service, expected_depth, False)
                    repeated = simulate_oracle(burst, arrival, service, expected_depth, False)
                    broken = simulate_oracle(burst, arrival, service, expected_depth, True)
                    self.assertEqual(healthy, repeated)
                    self.assertEqual(healthy["required_depth"], expected_depth)
                    self.assertEqual(healthy["analytic_depth"], expected_depth)
                    self.assertEqual(healthy["not_accepted_count"], 0)
                    self.assertEqual(broken["reference_after"], healthy["reference_after"])
                    self.assertEqual(broken["fault_active"], service > 0)
                    self.assertEqual(broken["fault_visible"], service > 0)
                    self.assertEqual(len(healthy["arrivals"]), 40)
                    self.assertLessEqual(healthy["offered_count"], 32)
                    self.assertLessEqual(healthy["required_depth"], 32)
                    if service == 0:
                        self.assertIsNone(healthy["reference_completion"])
                    else:
                        self.assertLessEqual(healthy["reference_completion"], 33)

    def test_malformed_inputs_reject_and_baseline_recovers(self):
        malformed = [
            (0, 3, 1, 17, False),
            (9, 3, 1, 17, False),
            (2.5, 3, 1, 17, False),
            ([8], 3, 1, 17, False),
            (math.nan, 3, 1, 17, False),
            (math.inf, 3, 1, 17, False),
            (True, 3, 1, 17, False),
            (8, 0, 1, 17, False),
            (8, 5, 1, 17, False),
            (8, 2.5, 1, 17, False),
            (8, 3, -1, 17, False),
            (8, 3, 5, 17, False),
            (8, 3, 0.5, 17, False),
            (8, 3, 1, -1, False),
            (8, 3, 1, 33, False),
            (8, 3, 1, 16.5, False),
            (8, 3, 1, 17, 2),
            (8, 3, 1, 17, 0.5),
            (8, 3, 1, 17, [False]),
        ]
        baseline = simulate_oracle()
        for arguments in malformed:
            with self.subTest(arguments=arguments):
                with self.assertRaises(ValueError):
                    simulate_oracle(*arguments)
                self.assertEqual(simulate_oracle(), baseline)
        simulate_oracle(8, 4, 1, 32, False)
        simulate_oracle(8, 4, 0, 32, False)
        simulate_oracle(8, 3, 1, 17, True)
        self.assertEqual(simulate_oracle(), baseline)


class P12ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "curriculum/modules.json").read_text(encoding="utf-8")
        )
        cls.text = {
            name: (MODULE / name).read_text(encoding="utf-8") for name in ARTIFACTS
        }

    def test_permanent_manifest_identity_and_prerequisite(self):
        p12 = next(module for module in self.manifest["modules"] if module["id"] == "P12")
        p11 = next(module for module in self.manifest["modules"] if module["id"] == "P11")
        self.assertEqual(p12["number"], 12)
        self.assertEqual(p12["title"], "Size a FIFO from Burst and Service Rates")
        self.assertEqual(p12["guiding_question"], QUESTION)
        self.assertEqual(p12["phase"], 3)
        self.assertEqual(p12["phase_title"], "Streaming architectures")
        self.assertEqual(
            p12["folder"], "modules/12-size-a-fifo-from-burst-and-service-rates"
        )
        self.assertEqual(p12["implementation_batch"], "P12")
        self.assertEqual(p12["prerequisites"], ["P11"])
        self.assertEqual(p12["status"], "implemented")
        self.assertEqual(p12["evidence_level"], "simulated")
        self.assertEqual(p11["status"], "implemented")

    def test_learning_slice_is_complete_concept_first_and_prerequisite_linked(self):
        self.assertEqual(set(ARTIFACTS), {path.name for path in MODULE.iterdir() if path.is_file()})
        for name, text in self.text.items():
            with self.subTest(name=name):
                self.assertTrue(text.strip())
                self.assertNotIn("TODO", text)
                self.assertNotIn("scaffolded", text.lower())
        for name in ("README.md", "lesson.m", "lesson.md", "checks.md"):
            self.assertIn(QUESTION, self.text[name])
        combined = "\n".join(self.text.values())
        self.assertIn("P11", combined)
        self.assertIn("P10", combined)
        self.assertIn("P01", combined)
        self.assertIn("registered", combined.lower())
        self.assertIn("non-fall-through", combined.lower())
        self.assertIn("one prompt at a time", combined.lower())
        self.assertIn("two-sentence teach-back", combined.lower())

        lesson = self.text["lesson.m"]
        ordered_markers = (
            "%% Read -",
            "%% Visualize baseline view 1",
            "%% Visualize baseline view 2",
            "%% Read the registered mechanism",
            "%% Move lever 1 only",
            "%% Read lever 1 mechanism",
            "%% Move lever 2 only",
            "%% Read lever 2 mechanism",
            "%% Deliberately broken case",
            "%% Explain, explore, check, and teach back",
        )
        positions = [lesson.index(marker) for marker in ordered_markers]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(lesson.lower().count("prediction:"), 1)

    def test_model_is_transparent_deterministic_bounded_and_presentation_free(self):
        model = self.text["model.m"]
        required = (
            "simulateUnbounded",
            "simulateFinite",
            "occupancyBefore",
            "occupancyAfter",
            "departedWords",
            "admittedWords",
            "notAcceptedWords",
            "requiredDepthWords",
            "analyticRequiredDepthWords",
            "fallThroughEstimateWords",
            "'faultVisible',brokenAssumeFallThrough &&",
            "A + (B-1)*max(A-S,0)",
            "recordCycleCount = 40",
            "maximumBurstWordCount",
            "P12:InvalidBurstCycles",
            "P12:InvalidArrivalRate",
            "P12:InvalidServiceRate",
            "P12:InvalidFifoDepth",
            "P12:InvalidBrokenAssumeFallThrough",
            "isnumeric(value)",
            "~islogical(value)",
            "isfinite(value)",
        )
        for token in required:
            self.assertIn(token, model)
        lowered = model.lower()
        forbidden = (
            "figure(",
            "plot(",
            "disp(",
            "fprintf(",
            "rand(",
            "randn(",
            "rng(",
            "global ",
            "persistent ",
            "fopen(",
            "webread(",
            "system(",
            "eval(",
            "feval(",
            "pause(",
            "timer(",
            "parfeval(",
            "while ",
            "dsp.",
            "timeseries(",
            "sim(",
        )
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, lowered)

    def test_experiment_has_two_isolated_sweeps_labels_metrics_and_one_broken_case(self):
        experiment = self.text["experiment.m"]
        self.assertNotIn("close all", experiment.lower())
        self.assertEqual(experiment.count("%% Sweep 1 -"), 1)
        self.assertEqual(experiment.count("%% Sweep 2 -"), 1)
        self.assertEqual(experiment.count("%% Broken case -"), 1)
        for token in (
            "burstCycleSweep = [1 2 4 6 8]",
            "serviceRateSweep = 0:4",
            "[3 5 9 13 17]",
            "[24 17 10 3 3]",
            "[NaN 25 13 9 9]",
            "model(8,3,1,17,true)",
            "notAcceptedWordCount == 1",
            "find(broken.applied.notAcceptedWords),8",
            "isequaln(broken.reference,healthy.reference)",
            "drawnow",
            "fprintf",
        ):
            self.assertIn(token, experiment)
        for unit in ("[cycles]", "[words]", "[words/cycle]", "[clock cycle]"):
            self.assertIn(unit, experiment)
        self.assertIn("must hold arrival rate, service, depth, and fault fixed", experiment)
        self.assertIn("must hold burst, arrival rate, depth, and fault fixed", experiment)

    def test_interactive_controls_are_bounded_model_backed_and_fault_explicit(self):
        interactive = self.text["interactive.m"]
        for token in (
            "uifigure",
            "uiaxes",
            "uispinner",
            "uicheckbox",
            "ValueChangedFcn",
            "modelFcn = @model",
            "'Limits',[1 8]",
            "'Limits',[1 4]",
            "'Limits',[0 4]",
            "'Limits',[0 32]",
            "'Limits',[1 40]",
            "Use broken depth estimate",
            "depthSpinner.Enable = 'off'",
            "conditional loss if ignored",
            "not BRAM, timing, or measured throughput",
            "delete(findall(groot,'Type','figure','Name',figureName))",
        ):
            self.assertIn(token, interactive)
        self.assertEqual(interactive.count("'RoundFractionalValues','on'"), 5)
        self.assertNotIn("close all", interactive.lower())
        self.assertNotIn("delete all", interactive.lower())

    def test_checks_cover_equations_limits_fault_validation_recovery_and_bounds(self):
        matlab_checks = self.text["run_checks.m"]
        tutor_checks = self.text["checks.md"]
        for token in (
            "P12:BaselineDeterminism",
            "P12:ReferenceConservation",
            "P12:FiniteConservation",
            "P12:OneWordShort",
            "P12:ZeroDepthRegisteredBoundary",
            "P12:BurstSweepDepths",
            "P12:ServiceSweepResults",
            "P12:NoServiceLimit",
            "P12:RegisteredStagingLimit",
            "P12:BrokenFallThrough",
            "P12:BrokenInertLimit",
            "P12:TypedInputEquivalence",
            "P12:HealthyGrid",
            "P12:FaultGrid",
            "P12:ResourceBound",
            "P12:BoundedNoDrain",
            "P12:BoundedCompletion",
            "P12:DeterminismRecovery",
            "~oneWordShort.faultVisible",
            "assertRejects",
            "for burstCycles = 1:8",
            "for arrivalRate = 1:4",
            "for serviceRate = 0:4",
        ):
            self.assertIn(token, matlab_checks)
        for identifier in (
            "P12:InvalidBurstCycles",
            "P12:InvalidArrivalRate",
            "P12:InvalidServiceRate",
            "P12:InvalidFifoDepth",
            "P12:InvalidBrokenAssumeFallThrough",
        ):
            self.assertGreaterEqual(matlab_checks.count(identifier), 2)
        for concept in (
            "unbounded",
            "conservation",
            "zero service",
            "same-edge",
            "backpressure",
            "conditional loss",
            "malformed",
            "recovery",
            "timeout",
            "cancellation",
            "teach-back",
        ):
            self.assertIn(concept, tutor_checks.lower())

    def test_p12_text_files_have_exactly_one_terminal_newline(self):
        for name in ARTIFACTS:
            with self.subTest(name=name):
                raw = (MODULE / name).read_bytes()
                self.assertTrue(raw.endswith(b"\n"))
                self.assertFalse(raw.endswith(b"\n\n"))
                self.assertNotIn(b"\r", raw)


if __name__ == "__main__":
    unittest.main()
