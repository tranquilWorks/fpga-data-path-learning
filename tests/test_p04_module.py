from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_FOLDER = ROOT / "modules/04-control-behavior-with-a-finite-state-machine"
GUIDING_QUESTION = (
    "What inputs, observable effects, and failure modes matter when you control "
    "Behavior with a Finite-State Machine?"
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


class P04ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "curriculum/modules.json").read_text(encoding="utf-8")
        )
        cls.module = next(module for module in cls.manifest["modules"] if module["id"] == "P04")

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
                "number": 4,
                "id": "P04",
                "title": "Control Behavior with a Finite-State Machine",
                "guiding_question": GUIDING_QUESTION,
                "phase": 1,
                "phase_title": "Digital logic",
                "slug": "control-behavior-with-a-finite-state-machine",
                "folder": "modules/04-control-behavior-with-a-finite-state-machine",
                "implementation_batch": "P04",
                "prerequisites": ["P03"],
                "status": "implemented",
                "evidence_level": "simulated",
            },
        )
        p03 = next(module for module in self.manifest["modules"] if module["id"] == "P03")
        self.assertEqual(p03["status"], "implemented")
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
        for marker in (
            "p03",
            "register",
            "current state",
            "next state",
            "pre-edge",
            "post-edge",
        ):
            self.assertIn(marker, lesson)
        for marker in ("read", "baseline", "lever 1", "lever 2", "mechanism first"):
            self.assertIn(marker, lesson)
        self.assertIn("make no second prediction", lesson)
        self.assertIn("make no second prediction", walkthrough)
        self.assertIn("one prompt at a time", checks)
        self.assertIn("teach-back", checks)
        self.assertIn("two sentences", checks)
        for limitation in ("setup/hold", "metastability", "not physical"):
            self.assertIn(limitation, lesson)

    def test_model_is_transparent_deterministic_bounded_and_presentation_free(self):
        source = self.read("model.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        for expression in (
            "cycle=(1:16).';",
            "startCycle=2;",
            "reset=cycle==1;",
            "start=cycle==startCycle;",
            "workDone=cycle==startCycle+completionDelay;",
            "deadlineExpired=cycle==startCycle+timeoutLimit;",
            "ifreset(cycleIndex)nextState=IDLE;correctNextState=IDLE;",
            "stateAfter(cycleIndex)=nextState;",
            "referenceStateAfter(cycleIndex)=correctNextState;",
            "busy=stateAfter==WAIT;",
            "donePulse=stateAfter==DONE;",
            "timeoutPulse=stateAfter==TIMEOUT;",
            "mismatchMask=stateAfter~=referenceStateAfter;",
            "lateWorkDoneMask=workDone&stateBefore~=WAIT;",
            "lateDeadlineMask=deadlineExpired&stateBefore~=WAIT;",
            "elseifcurrentState==DONE||currentState==TIMEOUTnextState=IDLE;",
            "validateIntegerScalar(completionDelay,1,8,'P04:InvalidCompletionDelay','completionDelay');",
            "validateIntegerScalar(timeoutLimit,1,8,'P04:InvalidTimeoutLimit','timeoutLimit');",
            "validateIntegerScalar(selectedCycle,1,16,'P04:InvalidSelectedCycle','selectedCycle');",
        ):
            self.assertIn(expression, compact)
        priority = (
            "ifbrokenPriorityifdeadlineExpirednextState=TIMEOUT;"
            "reason='brokenpriority:deadlinewins';elseifworkDone"
        )
        healthy_priority = (
            "elseifworkDonenextState=DONE;"
            "reason='completionwins:WAITtoDONE';elseifdeadlineExpired"
        )
        self.assertIn(priority, compact)
        self.assertIn(healthy_priority, compact)
        for field in (
            "stateBefore",
            "stateAfter",
            "referenceStateAfter",
            "transitionReason",
            "busy",
            "donePulse",
            "timeoutPulse",
            "terminalCycle",
            "mismatchCycles",
            "wrongTimeoutCount",
            "ignoredLateWorkDoneCount",
            "ignoredLateDeadlineCount",
            "modeledStateBits",
        ):
            self.assertIn(field, source)
        for scalar_cell_field in (
            "'stateLabels',{stateLabels}",
            "'stateName',{stateName}",
            "'referenceStateName',{referenceStateName}",
            "'transitionReason',{transitionReason}",
            "'referenceTransitionReason',{referenceTransitionReason}",
        ):
            self.assertIn(scalar_cell_field, compact)
        for identifier in (
            "P04:InvalidCompletionDelay",
            "P04:InvalidTimeoutLimit",
            "P04:InvalidSelectedCycle",
            "P04:InvalidBrokenPriority",
        ):
            self.assertIn(identifier, source)
        for validator in ("isnumeric", "islogical", "isreal", "isscalar", "isnan", "isinf", "fix"):
            self.assertIn(validator, lower)
        for presentation_call in ("figure", "plot", "stairs", "uifigure", "uiaxes", "disp", "fprintf"):
            self.assertIsNone(
                re.search(rf"\b{presentation_call}\s*\(", lower), presentation_call
            )
        for opaque_stateful_or_external in (
            "stateflow",
            "fi(",
            "dsp.",
            "hdl.",
            "sim(",
            "eval(",
            "feval(",
            "str2func(",
            "evalin(",
            "assignin(",
            "system(",
            "webread",
            "urlread",
            "fopen(",
            "load(",
            "save(",
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
        self.assertIn("completionDelays=1:6;", compact)
        self.assertIn("timeoutLimits=1:8;", compact)
        self.assertIn("model(completionDelays(sweepIndex),8,5,false)", compact)
        self.assertIn("model(4,timeoutLimits(sweepIndex),6,false)", compact)
        self.assertIn("completion-delay sweep must not move the deadline", lower)
        self.assertIn("timeout sweep must not move the completion input", lower)
        self.assertIn("deliberately broken case", lower)
        self.assertIn("healthyTie=model(4,4,6,false);", compact)
        self.assertIn("broken=model(4,4,6,true);", compact)
        self.assertIn("completion sampled on the deadline succeeds", lower)
        self.assertIn("broken.wrongtimeoutcount==1", compact.lower())
        self.assertGreaterEqual(lower.count("xlabel("), 8)
        self.assertGreaterEqual(lower.count("ylabel("), 8)
        for unit_marker in ("[cycles]", "[binary]", "[unitless]"):
            self.assertIn(unit_marker, lower)
        for metric in ("terminal state", "wait dwell", "busy for", "wrong timeout"):
            self.assertIn(metric, lower)
        self.assertNotIn("close all", lower)

    def test_signal_views_include_all_inputs_and_separate_overlapping_rows(self):
        for name, prefix in (
            ("lesson.m", "baseline"),
            ("experiment.m", "baseline"),
            ("interactive.m", "out"),
        ):
            with self.subTest(artifact=name):
                lower = self.read(name).lower()
                compact = re.sub(r"\s+", "", lower).replace("...", "")
                for signal in ("reset", "start", "workdone", "deadlineexpired"):
                    self.assertIn(f"{prefix}.{signal}", compact)
                self.assertIn("repmat(", lower)
                self.assertIn("vertically offset", lower)
        lesson_script = self.read("lesson.m").lower()
        experiment = self.read("experiment.m").lower()
        self.assertIn("reset timeout to 8 cycles and establish completion delay 3", lesson_script)
        self.assertGreaterEqual(experiment.count("[pulses]"), 2)

    def test_interactive_controls_are_bounded_model_backed_and_fault_safe(self):
        source = self.read("interactive.m")
        lower = source.lower()
        self.assertIn("modelFcn = @model", source)
        self.assertGreaterEqual(lower.count("uispinner("), 3)
        self.assertIn("uicheckbox(", lower)
        self.assertGreaterEqual(len(re.findall(r"'Limits'\s*,\s*\[\s*1\s+8\s*\]", source)), 2)
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*1\s+16\s*\]")
        self.assertGreaterEqual(source.count("ValueChangedFcn"), 4)
        self.assertIn("faultCheckbox.Enable = 'off'", source)
        self.assertIn("faultCheckbox.Value = false", source)
        self.assertIn("completionDelay ~= timeoutLimit", source)
        for phrase in (
            "pre-edge",
            "registered state",
            "completion on the deadline succeeds",
            "ignored late work/deadline pulses",
            "modeled state bits",
            "mismatches",
        ):
            self.assertIn(phrase, lower)
        self.assertNotIn("close all", lower)

    def test_checks_cover_transition_limits_fault_validation_and_recovery(self):
        source = self.read("run_checks.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "").lower()
        self.assertGreaterEqual(lower.count("assert("), 26)
        self.assertIn("expectedstate=[01112zeros(1,11)].';", compact)
        self.assertIn("expectedtimeouts=[11100000];", compact)
        self.assertIn("expectedterminalcycles=[34566666];", compact)
        self.assertIn("expectedbusycounts=[12344444];", compact)
        self.assertIn("healthytie=model(4,4,6,false);", compact)
        self.assertIn("brokentie=model(4,4,6,true);", compact)
        self.assertIn("fortiedelay=1:8", compact)
        self.assertIn(
            "currenthealthytie=model(tiedelay,tiedelay,tiecycle,false);", compact
        )
        self.assertIn(
            "currentbrokentie=model(tiedelay,tiedelay,tiecycle,true);", compact
        )
        for identifier in (
            "P04:BaselineStateTrace",
            "P04:PrePostEdgeConvention",
            "P04:MutuallyExclusiveOutputs",
            "P04:CompletionSweep",
            "P04:TimeoutSweep",
            "P04:OutcomeInvariant",
            "P04:LateCompletionIsolation",
            "P04:InclusiveDeadline",
            "P04:BrokenSymptom",
            "P04:EqualDelayPriorityGrid",
            "P04:EqualDelayFaultRecovery",
            "P04:BrokenInertLimit",
            "P04:ResourceBound",
            "P04:SelectedViewIsolation",
            "P04:DeterminismRecovery",
            "P04:InvalidCompletionDelay",
            "P04:InvalidTimeoutLimit",
            "P04:InvalidSelectedCycle",
            "P04:InvalidBrokenPriority",
        ):
            self.assertIn(identifier.lower(), lower)
        self.assertIn("p04 checks passed", lower)

    def test_p04_text_files_have_exactly_one_terminal_newline(self):
        for name in REQUIRED_ARTIFACTS:
            with self.subTest(artifact=name):
                data = (MODULE_FOLDER / name).read_bytes()
                self.assertTrue(data.endswith(b"\n"))
                self.assertFalse(data.endswith(b"\n\n"))
                self.assertNotIn(b"\r", data)


class P04IndependentOracleTests(unittest.TestCase):
    IDLE = 0
    WAIT = 1
    DONE = 2
    TIMEOUT = 3

    @classmethod
    def advance(cls, state, start, work_done, deadline, broken_priority):
        if state == cls.IDLE:
            return cls.WAIT if start else cls.IDLE
        if state == cls.WAIT:
            if broken_priority:
                if deadline:
                    return cls.TIMEOUT
                if work_done:
                    return cls.DONE
            else:
                if work_done:
                    return cls.DONE
                if deadline:
                    return cls.TIMEOUT
            return cls.WAIT
        if state in (cls.DONE, cls.TIMEOUT):
            return cls.IDLE
        raise AssertionError("invalid oracle state")

    @classmethod
    def oracle(cls, completion_delay=3, timeout_limit=5, selected_cycle=5, broken_priority=False):
        if type(completion_delay) is not int or not 1 <= completion_delay <= 8:
            raise ValueError("completion_delay")
        if type(timeout_limit) is not int or not 1 <= timeout_limit <= 8:
            raise ValueError("timeout_limit")
        if type(selected_cycle) is not int or not 1 <= selected_cycle <= 16:
            raise ValueError("selected_cycle")
        valid_flag = type(broken_priority) is bool or (
            type(broken_priority) is int and broken_priority in (0, 1)
        )
        if not valid_flag:
            raise ValueError("broken_priority")
        broken_priority = bool(broken_priority)

        cycles = list(range(1, 17))
        reset = [cycle == 1 for cycle in cycles]
        start = [cycle == 2 for cycle in cycles]
        work_done = [cycle == 2 + completion_delay for cycle in cycles]
        deadline = [cycle == 2 + timeout_limit for cycle in cycles]
        previous = cls.IDLE
        previous_reference = cls.IDLE
        before = []
        after = []
        reference_after = []

        for index in range(16):
            before.append(previous)
            if reset[index]:
                next_state = cls.IDLE
                reference_next = cls.IDLE
            else:
                next_state = cls.advance(
                    previous,
                    start[index],
                    work_done[index],
                    deadline[index],
                    broken_priority,
                )
                reference_next = cls.advance(
                    previous_reference,
                    start[index],
                    work_done[index],
                    deadline[index],
                    False,
                )
            after.append(next_state)
            reference_after.append(reference_next)
            previous = next_state
            previous_reference = reference_next

        busy = [state == cls.WAIT for state in after]
        done = [state == cls.DONE for state in after]
        timeout = [state == cls.TIMEOUT for state in after]
        mismatch = [actual != expected for actual, expected in zip(after, reference_after)]
        terminal_indices = [index for index, value in enumerate(done) if value] + [
            index for index, value in enumerate(timeout) if value
        ]
        terminal_index = min(terminal_indices)
        selected = selected_cycle - 1
        return {
            "reset": reset,
            "start": start,
            "work_done": work_done,
            "deadline": deadline,
            "before": before,
            "after": after,
            "reference_after": reference_after,
            "busy": busy,
            "done": done,
            "timeout": timeout,
            "mismatch_cycles": [index + 1 for index, value in enumerate(mismatch) if value],
            "wrong_timeout_cycles": [
                index + 1
                for index, (actual, expected) in enumerate(zip(after, reference_after))
                if actual == cls.TIMEOUT and expected == cls.DONE
            ],
            "terminal_cycle": terminal_index + 1,
            "busy_count": sum(busy),
            "completion_count": sum(done),
            "timeout_count": sum(timeout),
            "ignored_late_work": sum(
                pulse and state != cls.WAIT for pulse, state in zip(work_done, before)
            ),
            "ignored_late_deadline": sum(
                pulse and state != cls.WAIT for pulse, state in zip(deadline, before)
            ),
            "selected_before": before[selected],
            "selected_after": after[selected],
        }

    def test_exact_baseline_edge_convention_outputs_and_recovery(self):
        result = self.oracle()
        self.assertEqual(result["after"], [0, 1, 1, 1, 2] + [0] * 11)
        self.assertEqual([i + 1 for i, value in enumerate(result["busy"]) if value], [2, 3, 4])
        self.assertEqual([i + 1 for i, value in enumerate(result["done"]) if value], [5])
        self.assertEqual([i + 1 for i, value in enumerate(result["timeout"]) if value], [])
        self.assertEqual(result["terminal_cycle"], 5)
        self.assertEqual(result["busy_count"], 3)
        self.assertEqual(result["selected_before"], self.WAIT)
        self.assertEqual(result["selected_after"], self.DONE)
        self.assertEqual(result["after"][5], self.IDLE)
        self.assertEqual(result["ignored_late_deadline"], 1)

    def test_exhaustive_healthy_outcome_latency_outputs_and_resource_bound(self):
        for completion_delay in range(1, 9):
            for timeout_limit in range(1, 9):
                result = self.oracle(completion_delay, timeout_limit, 16, False)
                expected_success = completion_delay <= timeout_limit
                terminal_cycle = 2 + min(completion_delay, timeout_limit)
                with self.subTest(completion_delay=completion_delay, timeout_limit=timeout_limit):
                    self.assertEqual(result["completion_count"], int(expected_success))
                    self.assertEqual(result["timeout_count"], int(not expected_success))
                    self.assertEqual(result["terminal_cycle"], terminal_cycle)
                    self.assertEqual(result["busy_count"], min(completion_delay, timeout_limit))
                    self.assertEqual(result["after"][terminal_cycle], self.IDLE)
                    self.assertTrue(all(state in range(4) for state in result["after"]))
                    self.assertEqual(len(result["after"]), 16)
                    self.assertTrue(
                        all(sum(outputs) <= 1 for outputs in zip(result["busy"], result["done"], result["timeout"]))
                    )

    def test_two_sweep_limits_are_independent(self):
        completion_results = [self.oracle(delay, 8) for delay in range(1, 7)]
        self.assertEqual([result["busy_count"] for result in completion_results], list(range(1, 7)))
        self.assertEqual([result["terminal_cycle"] for result in completion_results], list(range(3, 9)))
        self.assertEqual([result["completion_count"] for result in completion_results], [1] * 6)
        timeout_results = [self.oracle(4, limit) for limit in range(1, 9)]
        self.assertEqual([result["timeout_count"] for result in timeout_results], [1, 1, 1, 0, 0, 0, 0, 0])
        self.assertEqual([result["terminal_cycle"] for result in timeout_results], [3, 4, 5, 6, 6, 6, 6, 6])
        self.assertEqual([result["busy_count"] for result in timeout_results], [1, 2, 3, 4, 4, 4, 4, 4])

    def test_broken_priority_boundary_symptom_and_inert_limit(self):
        healthy = self.oracle(4, 4, 6, False)
        broken = self.oracle(4, 4, 6, True)
        self.assertEqual(healthy["after"][5], self.DONE)
        self.assertEqual(broken["after"][5], self.TIMEOUT)
        self.assertEqual(broken["mismatch_cycles"], [6])
        self.assertEqual(broken["wrong_timeout_cycles"], [6])
        self.assertEqual(broken["after"][6], self.IDLE)
        for completion_delay in range(1, 9):
            for timeout_limit in range(1, 9):
                if completion_delay != timeout_limit:
                    with self.subTest(completion_delay=completion_delay, timeout_limit=timeout_limit):
                        result = self.oracle(completion_delay, timeout_limit, 5, True)
                        self.assertEqual(result["mismatch_cycles"], [])

    def test_broken_priority_activates_and_recovers_at_every_equal_delay(self):
        for delay in range(1, 9):
            terminal_cycle = 2 + delay
            healthy = self.oracle(delay, delay, terminal_cycle, False)
            broken = self.oracle(delay, delay, terminal_cycle, True)
            terminal_index = terminal_cycle - 1
            with self.subTest(delay=delay):
                self.assertTrue(healthy["done"][terminal_index])
                self.assertFalse(healthy["timeout"][terminal_index])
                self.assertFalse(broken["done"][terminal_index])
                self.assertTrue(broken["timeout"][terminal_index])
                self.assertEqual(broken["mismatch_cycles"], [terminal_cycle])
                self.assertEqual(broken["wrong_timeout_cycles"], [terminal_cycle])
                self.assertEqual(broken["reference_after"], healthy["after"])
                self.assertEqual(broken["after"][terminal_index + 1], self.IDLE)

    def test_late_events_and_selected_cycle_are_isolated(self):
        success = self.oracle(1, 8)
        timed_out = self.oracle(8, 1)
        tie = self.oracle(4, 4)
        self.assertEqual((success["ignored_late_work"], success["ignored_late_deadline"]), (0, 1))
        self.assertEqual((timed_out["ignored_late_work"], timed_out["ignored_late_deadline"]), (1, 0))
        self.assertEqual((tie["ignored_late_work"], tie["ignored_late_deadline"]), (0, 0))
        first = self.oracle(3, 5, 1)
        last = self.oracle(3, 5, 16)
        for field in ("reset", "start", "work_done", "deadline", "before", "after", "busy", "done", "timeout"):
            self.assertEqual(first[field], last[field])

    def test_malformed_inputs_reject_and_valid_call_recovers(self):
        invalid_calls = (
            (0, 5, 5, False),
            (9, 5, 5, False),
            (2.5, 5, 5, False),
            ([2, 3], 5, 5, False),
            (math.nan, 5, 5, False),
            (math.inf, 5, 5, False),
            (1 + 0j, 5, 5, False),
            (True, 5, 5, False),
            (3, 0, 5, False),
            (3, 9, 5, False),
            (3, 2.5, 5, False),
            (3, [4, 5], 5, False),
            (3, math.nan, 5, False),
            (3, math.inf, 5, False),
            (3, 1 + 0j, 5, False),
            (3, True, 5, False),
            (3, 5, 0, False),
            (3, 5, 17, False),
            (3, 5, 2.5, False),
            (3, 5, [4, 5], False),
            (3, 5, math.nan, False),
            (3, 5, math.inf, False),
            (3, 5, 1 + 0j, False),
            (3, 5, True, False),
            (3, 5, 5, 2),
            (3, 5, 5, 0.5),
            (3, 5, 5, [False, True]),
            (3, 5, 5, math.nan),
            (3, 5, 5, math.inf),
            (3, 5, 5, 1 + 0j),
        )
        expected = self.oracle()
        for arguments in invalid_calls:
            with self.subTest(arguments=arguments):
                with self.assertRaises(ValueError):
                    self.oracle(*arguments)
                self.assertEqual(self.oracle(), expected)

    def test_determinism_call_isolation_and_fixed_allocation(self):
        baseline = self.oracle(6, 7, 12, False)
        for completion_delay in range(1, 9):
            for timeout_limit in range(1, 9):
                current = self.oracle(completion_delay, timeout_limit, 16, False)
                self.assertEqual(len(current["before"]), 16)
                self.assertEqual(len(current["after"]), 16)
                self.assertEqual(len(current["reference_after"]), 16)
                self.assertLessEqual(len(set(current["after"])), 4)
        self.oracle(8, 8, 16, True)
        self.assertEqual(self.oracle(6, 7, 12, False), baseline)


if __name__ == "__main__":
    unittest.main()
