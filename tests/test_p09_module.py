from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_FOLDER = ROOT / "modules/09-handshake-with-valid-and-ready"
GUIDING_QUESTION = (
    "What inputs, observable effects, and failure modes matter when you handshake "
    "with Valid and Ready?"
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
TOKEN_CODES = [0, 411, 822, 1233, 1644, 2055, 2466, 2877]


class P09ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "curriculum/modules.json").read_text(encoding="utf-8")
        )
        cls.module = next(
            module for module in cls.manifest["modules"] if module["id"] == "P09"
        )

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
                "number": 9,
                "id": "P09",
                "title": "Handshake with Valid and Ready",
                "guiding_question": GUIDING_QUESTION,
                "phase": 3,
                "phase_title": "Streaming architectures",
                "slug": "handshake-with-valid-and-ready",
                "folder": "modules/09-handshake-with-valid-and-ready",
                "implementation_batch": "P09",
                "prerequisites": ["P08"],
                "status": "implemented",
                "evidence_level": "simulated",
            },
        )
        p08 = next(
            module for module in self.manifest["modules"] if module["id"] == "P08"
        )
        self.assertEqual(p08["status"], "implemented")
        names = {path.name for path in MODULE_FOLDER.iterdir() if path.is_file()}
        self.assertTrue(REQUIRED_ARTIFACTS <= names)
        for name in REQUIRED_ARTIFACTS:
            with self.subTest(artifact=name):
                self.assertGreater((MODULE_FOLDER / name).stat().st_size, 0)

    def test_learning_slice_is_complete_concept_first_and_prerequisite_linked(self):
        combined = "\n".join(self.read(name) for name in REQUIRED_ARTIFACTS).lower()
        for placeholder in ("scaffolded", "todo", "tbd", "implement model.m"):
            self.assertNotIn(placeholder, combined)
        for name in ("README.md", "lesson.m", "lesson.md", "checks.md"):
            with self.subTest(artifact=name):
                self.assertIn(GUIDING_QUESTION, self.read(name))
        lesson = self.read("lesson.md").lower()
        walkthrough = self.read("walkthrough.md").lower()
        checks = self.read("checks.md").lower()
        for marker in (
            "p08",
            "producer owns",
            "consumer owns",
            "valid",
            "ready",
            "transfer[n]",
            "stable",
            "rising edge",
            "12-bit phase codes",
        ):
            self.assertIn(marker, lesson)
        for marker in (
            "learning cycle",
            "baseline",
            "lever 1",
            "lever 2",
            "mechanism first",
            "deliberately broken case",
        ):
            self.assertIn(marker, lesson)
        self.assertIn("make no second prediction", lesson)
        self.assertIn("make no second prediction", walkthrough)
        self.assertIn("one prompt at a time", checks)
        self.assertIn("limiting-case check", checks)
        self.assertIn("interpretation and transfer check", checks)
        self.assertIn("teach-back", checks)
        self.assertIn("two sentences", checks)
        for limitation in (
            "free-running nco",
            "clock-domain crossing",
            "fifo",
            "synthesis",
            "measured throughput",
        ):
            self.assertIn(limitation, lesson)

    def test_model_is_transparent_deterministic_bounded_and_presentation_free(self):
        source = self.read("model.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        for expression in (
            "payloadAccumulatorBits=12;",
            "payloadModulus=2^payloadAccumulatorBits;",
            "payloadTuningWord=411;",
            "tokenCount=8;",
            "recordCycleCount=35;",
            "readyStallStartCycle=5;",
            "tokenCodes=mod(tokenOrdinal*payloadTuningWord,payloadModulus);",
            "ready(readyStallStartCycle:readyStallEndCycle)=false;",
            "transfer(cycleIndex)=currentValid&&ready(cycleIndex);",
            "elseifcurrentValid&&~ready(cycleIndex)&&brokenMode",
            "holdViolation(cycleIndex)=~valid(cycleIndex)||",
        ):
            self.assertIn(expression, compact)
        for field in (
            "reference",
            "applied",
            "valid",
            "ready",
            "transfer",
            "stalledValid",
            "acceptedTokenIndices",
            "acceptedDataCodes",
            "firstOfferCycle",
            "transferCycle",
            "waitCycles",
            "dropEvent",
            "holdViolation",
            "lostTokenCount",
            "duplicateTokenCount",
            "outOfOrderCount",
            "completionCycle",
            "activeWindowTransferRate",
            "maxRecordCycles",
            "maxTokenCount",
            "modeledPayloadHoldBits",
        ):
            self.assertIn(field, source)
        for identifier in (
            "P09:InvalidSourceGapCycles",
            "P09:InvalidReadyStallCycles",
            "P09:InvalidBrokenAdvanceWithoutReady",
        ):
            self.assertIn(identifier, source)
        for validator in (
            "isnumeric",
            "islogical",
            "isreal",
            "isscalar",
            "isnan",
            "isinf",
            "fix",
        ):
            self.assertIn(validator, lower)
        for presentation_call in (
            "figure",
            "plot",
            "stairs",
            "stem",
            "scatter",
            "uifigure",
            "uiaxes",
            "disp",
            "fprintf",
        ):
            self.assertIsNone(
                re.search(rf"\b{presentation_call}\s*\(", lower),
                presentation_call,
            )
        for opaque_stateful_external_or_async in (
            "dsp.",
            "comm.",
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
        ):
            self.assertNotIn(opaque_stateful_external_or_async, lower)
        self.assertIsNone(re.search(r"(?m)^\s*while\b", lower))

    def test_accepted_numeric_classes_have_behavioral_equivalence_check(self):
        compact_model = re.sub(r"\s+", "", self.read("model.m")).replace("...", "")
        for conversion in (
            "sourceGapCycles=double(sourceGapCycles);",
            "readyStallCycles=double(readyStallCycles);",
            "brokenAdvanceWithoutReady=logical(brokenAdvanceWithoutReady);",
        ):
            self.assertIn(conversion, compact_model)
        compact_checks = re.sub(r"\s+", "", self.read("run_checks.m")).replace(
            "...", ""
        )
        self.assertIn(
            "typedBaseline=model(uint8(1),uint8(3),uint8(0));",
            compact_checks,
        )
        self.assertIn("isequaln(typedBaseline,baseline)", compact_checks)
        self.assertIn("P09:NumericClassNormalization", self.read("run_checks.m"))

    def test_experiment_has_independent_sweeps_labels_metrics_and_broken_case(self):
        source = self.read("experiment.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        self.assertGreaterEqual(source.count("%%"), 16)
        self.assertIn("sweep 1", lower)
        self.assertIn("sweep 2", lower)
        self.assertIn("sourceGapSweep=0:3;", compact)
        self.assertIn("readyStallSweep=0:6;", compact)
        self.assertIn("model(sourceGapSweep(sweepIndex),0,false)", compact)
        self.assertIn("model(0,readyStallSweep(sweepIndex),false)", compact)
        self.assertIn("source-gap sweep must preserve", lower)
        self.assertIn("ready-stall sweep must preserve", lower)
        self.assertIn("deliberately broken case", lower)
        self.assertIn("healthy=model(0,3,false);", compact)
        self.assertIn("broken=model(0,3,true);", compact)
        self.assertIn("advance producer state without ready", lower)
        self.assertIn("broken.applied.lostTokenCount==3", compact)
        self.assertGreaterEqual(lower.count("drawnow"), 16)
        self.assertIn("run one section at a time", lower)
        self.assertGreaterEqual(lower.count("xlabel("), 16)
        self.assertGreaterEqual(lower.count("ylabel("), 16)
        for unit_marker in (
            "[cycles]",
            "[binary, vertically offset]",
            "[unsigned 12-bit phase code]",
            "[tokens]",
            "[transfers/cycle]",
        ):
            self.assertIn(unit_marker, lower)
        for metric in (
            "completion",
            "source bubbles",
            "stalled-valid",
            "maximum wait",
            "transfer rate",
            "lost",
            "hold violation",
        ):
            self.assertIn(metric, lower)
        self.assertNotIn("close all", lower)

    def test_interactive_controls_are_bounded_model_backed_and_fault_safe(self):
        source = self.read("interactive.m")
        lower = source.lower()
        self.assertIn("modelFcn = @model", source)
        self.assertGreaterEqual(lower.count("uispinner("), 3)
        self.assertIn("uicheckbox(", lower)
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*0\s+3\s*\]")
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*0\s+6\s*\]")
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*1\s+35\s*\]")
        self.assertGreaterEqual(source.count("ValueChangedFcn"), 4)
        self.assertIn("readyStallCycles == 0", source)
        clear_fault = source.index("faultCheckbox.Value = false")
        disable_fault = source.index("faultCheckbox.Enable = 'off'")
        self.assertLess(clear_fault, disable_fault)
        for phrase in (
            "transfer occurs only",
            "source gap",
            "ready-low duration",
            "accepted/lost/dropped/hold",
            "35-cycle trace",
            "not achieved timing",
        ):
            self.assertIn(phrase, lower)
        self.assertIn("out.reference.dataCode", source)
        self.assertIn("out.applied.dataCode", source)
        self.assertIn("out.applied.transfer", source)
        self.assertNotIn("close all", lower)

    def test_checks_cover_truth_limits_fault_validation_recovery_and_bounds(self):
        source = self.read("run_checks.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "").lower()
        self.assertGreaterEqual(lower.count("assert("), 25)
        self.assertIn("expectedtokencodes=[041182212331644205524662877].';", compact)
        self.assertIn("sourcegapsweep=0:3;", compact)
        self.assertIn("readystallsweep=0:6;", compact)
        self.assertIn("forsourcegapcycles=0:3", compact)
        self.assertIn("forreadystallcycles=0:6", compact)
        self.assertIn("readylowduringbubbles=model(2,2,false);", compact)
        self.assertIn("partialreadyoverlap=model(2,3,false);", compact)
        for identifier in (
            "P09:BaselineSignals",
            "P09:BaselineTokenAccounting",
            "P09:NumericClassNormalization",
            "P09:TruthTableCoverage",
            "P09:TransferTruthTable",
            "P09:HealthyHoldRule",
            "P09:SourceGapSweep",
            "P09:SourceGapSweepIsolation",
            "P09:ReadyStallSweep",
            "P09:ReadyStallSweepIsolation",
            "P09:ReadyLowDuringSourceBubbles",
            "P09:PartialReadySourceOverlap",
            "P09:AlwaysReadyLimit",
            "P09:LongestStallLimit",
            "P09:SparseSourceLimit",
            "P09:FinalRecordEdgeLimit",
            "P09:BrokenAdvanceLoss",
            "P09:BrokenReferenceIsolation",
            "P09:BrokenInertLimit",
            "P09:HealthyGrid",
            "P09:BrokenGrid",
            "P09:ResourceBound",
            "P09:DeterminismRecovery",
            "P09:InvalidSourceGapCycles",
            "P09:InvalidReadyStallCycles",
            "P09:InvalidBrokenAdvanceWithoutReady",
        ):
            self.assertIn(identifier.lower(), lower)
        self.assertIn("p09 checks passed", lower)

    def test_p09_text_files_have_exactly_one_terminal_newline(self):
        for name in REQUIRED_ARTIFACTS:
            with self.subTest(artifact=name):
                data = (MODULE_FOLDER / name).read_bytes()
                self.assertTrue(data.endswith(b"\n"))
                self.assertFalse(data.endswith(b"\n\n"))
                self.assertNotIn(b"\r", data)


class P09IndependentOracleTests(unittest.TestCase):
    @staticmethod
    def oracle(
        source_gap_cycles: int = 1,
        ready_stall_cycles: int = 3,
        broken_advance: bool = False,
    ):
        if type(source_gap_cycles) is not int or not 0 <= source_gap_cycles <= 3:
            raise ValueError("source_gap_cycles")
        if type(ready_stall_cycles) is not int or not 0 <= ready_stall_cycles <= 6:
            raise ValueError("ready_stall_cycles")
        valid_flag = type(broken_advance) is bool or (
            type(broken_advance) is int and broken_advance in (0, 1)
        )
        if not valid_flag:
            raise ValueError("broken_advance")
        broken_advance = bool(broken_advance)

        record_cycles = 35
        token_count = 8
        ready = [True] * record_cycles
        for cycle in range(5, 5 + ready_stall_cycles):
            ready[cycle - 1] = False

        def simulate(broken: bool):
            valid = [False] * record_cycles
            data = [None] * record_cycles
            offered_id = [0] * record_cycles
            transfer = [False] * record_cycles
            accepted_data_by_cycle = [None] * record_cycles
            accepted_id_by_cycle = [0] * record_cycles
            drops = [False] * record_cycles
            first_offer = [None] * token_count
            transfer_cycle = [None] * token_count

            current_id = 1
            current_data = TOKEN_CODES[0]
            current_valid = True
            gap_remaining = 0
            exhausted = False

            def advance():
                nonlocal current_id, current_data, current_valid
                nonlocal gap_remaining, exhausted
                if current_id < token_count:
                    current_id += 1
                    current_data = TOKEN_CODES[current_id - 1]
                    if source_gap_cycles == 0:
                        current_valid = True
                        gap_remaining = 0
                    else:
                        current_valid = False
                        gap_remaining = source_gap_cycles
                    exhausted = False
                else:
                    current_valid = False
                    gap_remaining = 0
                    exhausted = True

            for index in range(record_cycles):
                valid[index] = current_valid
                if current_valid:
                    data[index] = current_data
                    offered_id[index] = current_id
                    if first_offer[current_id - 1] is None:
                        first_offer[current_id - 1] = index + 1
                transfer[index] = current_valid and ready[index]
                if transfer[index]:
                    accepted_data_by_cycle[index] = current_data
                    accepted_id_by_cycle[index] = current_id
                    transfer_cycle[current_id - 1] = index + 1
                    advance()
                elif current_valid and not ready[index] and broken:
                    drops[index] = True
                    advance()
                elif not current_valid and not exhausted:
                    if gap_remaining > 1:
                        gap_remaining -= 1
                    elif gap_remaining == 1:
                        gap_remaining = 0
                        current_valid = True

            hold_violations = [False] * record_cycles
            for index in range(1, record_cycles):
                if valid[index - 1] and not ready[index - 1]:
                    hold_violations[index] = not (
                        valid[index]
                        and offered_id[index] == offered_id[index - 1]
                        and data[index] == data[index - 1]
                    )

            accepted_ids = [value for value in accepted_id_by_cycle if value]
            accepted_data = [
                value for value in accepted_data_by_cycle if value is not None
            ]
            lost_ids = [
                token_id
                for token_id in range(1, token_count + 1)
                if token_id not in accepted_ids
            ]
            completed = len(accepted_ids) == token_count and not lost_ids
            completion = (
                max(index + 1 for index, event in enumerate(transfer) if event)
                if completed
                else None
            )
            active_cycles = completion if completed else record_cycles
            wait_cycles = [
                None if transfer_at is None else transfer_at - offer_at
                for offer_at, transfer_at in zip(first_offer, transfer_cycle)
            ]
            observed_waits = [value for value in wait_cycles if value is not None]
            return {
                "valid": valid,
                "data": data,
                "offered_id": offered_id,
                "ready": ready,
                "transfer": transfer,
                "stalled": [v and not r for v, r in zip(valid, ready)],
                "ready_without_valid": [
                    not v and r for v, r in zip(valid, ready)
                ],
                "neither": [not v and not r for v, r in zip(valid, ready)],
                "accepted_ids": accepted_ids,
                "accepted_data": accepted_data,
                "first_offer": first_offer,
                "transfer_cycle": transfer_cycle,
                "wait_cycles": wait_cycles,
                "drops": drops,
                "hold_violations": hold_violations,
                "lost_ids": lost_ids,
                "completed": completed,
                "completion": completion,
                "active_cycles": active_cycles,
                "active_rate": len(accepted_ids) / active_cycles,
                "active_stalls": sum(
                    v and not r
                    for v, r in zip(valid[:active_cycles], ready[:active_cycles])
                ),
                "active_bubbles": sum(not v for v in valid[:active_cycles]),
                "maximum_wait": max(observed_waits) if observed_waits else None,
                "drop_count": sum(drops),
                "hold_violation_count": sum(hold_violations),
                "record_values": len(valid),
                "token_values": len(TOKEN_CODES),
            }

        reference = simulate(False)
        applied = simulate(broken_advance)
        return {
            "source_gap": source_gap_cycles,
            "ready_stall": ready_stall_cycles,
            "broken": broken_advance,
            "ready": ready,
            "token_codes": TOKEN_CODES.copy(),
            "reference": reference,
            "applied": applied,
            "fault_active": broken_advance and applied["drop_count"] > 0,
            "record_cycles": record_cycles,
            "token_count": token_count,
            "payload_bits": 12,
        }

    def test_exact_baseline_signals_payloads_waits_and_metrics(self):
        result = self.oracle()
        path = result["applied"]
        self.assertEqual(result["token_codes"], TOKEN_CODES)
        self.assertEqual(
            [index + 1 for index, event in enumerate(path["valid"]) if event],
            [1, 3, 5, 6, 7, 8, 10, 12, 14, 16, 18],
        )
        self.assertEqual(
            [index + 1 for index, event in enumerate(path["transfer"]) if event],
            [1, 3, 8, 10, 12, 14, 16, 18],
        )
        self.assertEqual(path["data"][4:8], [822] * 4)
        self.assertEqual(path["accepted_ids"], list(range(1, 9)))
        self.assertEqual(path["accepted_data"], TOKEN_CODES)
        self.assertEqual(path["first_offer"], [1, 3, 5, 10, 12, 14, 16, 18])
        self.assertEqual(path["transfer_cycle"], [1, 3, 8, 10, 12, 14, 16, 18])
        self.assertEqual(path["wait_cycles"], [0, 0, 3, 0, 0, 0, 0, 0])
        self.assertEqual((path["completion"], path["active_stalls"]), (18, 3))
        self.assertEqual(path["active_bubbles"], 7)
        self.assertEqual(path["active_rate"], 8 / 18)
        self.assertEqual(path["lost_ids"], [])
        self.assertEqual(path["hold_violation_count"], 0)
        self.assertEqual(result["reference"], path)

    def test_truth_table_and_stalled_successor_stability(self):
        path = self.oracle(2, 3, False)["applied"]
        categories_seen = set()
        for valid, ready, transfer, neither, ready_only, stalled in zip(
            path["valid"],
            path["ready"],
            path["transfer"],
            path["neither"],
            path["ready_without_valid"],
            path["stalled"],
        ):
            self.assertEqual(transfer, valid and ready)
            self.assertEqual(sum((neither, ready_only, stalled, transfer)), 1)
            categories_seen.add((valid, ready))
        self.assertEqual(
            categories_seen, {(False, False), (False, True), (True, False), (True, True)}
        )
        for index in range(1, 35):
            if path["valid"][index - 1] and not path["ready"][index - 1]:
                self.assertTrue(path["valid"][index])
                self.assertEqual(path["offered_id"][index], path["offered_id"][index - 1])
                self.assertEqual(path["data"][index], path["data"][index - 1])
        self.assertFalse(any(path["hold_violations"]))

    def test_source_gap_sweep_changes_bubbles_not_ready_payload_or_order(self):
        results = [self.oracle(gap, 0, False) for gap in range(4)]
        self.assertEqual(
            [result["applied"]["completion"] for result in results],
            [8, 15, 22, 29],
        )
        self.assertEqual(
            [result["applied"]["active_bubbles"] for result in results],
            [0, 7, 14, 21],
        )
        for result in results:
            path = result["applied"]
            self.assertTrue(all(result["ready"]))
            self.assertEqual(path["accepted_ids"], list(range(1, 9)))
            self.assertEqual(path["accepted_data"], TOKEN_CODES)
            self.assertEqual(path["active_stalls"], 0)
            self.assertEqual(path["active_rate"], 8 / path["completion"])

    def test_ready_stall_sweep_changes_wait_not_source_payload_or_order(self):
        results = [self.oracle(0, stall, False) for stall in range(7)]
        self.assertEqual(
            [result["applied"]["completion"] for result in results],
            list(range(8, 15)),
        )
        self.assertEqual(
            [result["applied"]["active_stalls"] for result in results],
            list(range(7)),
        )
        self.assertEqual(
            [result["applied"]["maximum_wait"] for result in results],
            list(range(7)),
        )
        for stall, result in enumerate(results):
            path = result["applied"]
            self.assertEqual(path["accepted_ids"], list(range(1, 9)))
            self.assertEqual(path["accepted_data"], TOKEN_CODES)
            self.assertEqual(path["active_bubbles"], 0)
            self.assertFalse(any(path["hold_violations"]))
            self.assertEqual(sum(not ready for ready in result["ready"]), stall)

    def test_ready_low_delays_only_cycles_that_overlap_a_valid_offer(self):
        hidden = self.oracle(2, 2, False)["applied"]
        self.assertEqual(
            [index + 1 for index, event in enumerate(hidden["transfer"]) if event],
            [1, 4, 7, 10, 13, 16, 19, 22],
        )
        self.assertEqual(
            [index + 1 for index, event in enumerate(hidden["neither"]) if event],
            [5, 6],
        )
        self.assertEqual(hidden["active_stalls"], 0)
        self.assertEqual(hidden["maximum_wait"], 0)
        self.assertEqual(hidden["completion"], 22)
        self.assertEqual(hidden["active_bubbles"], 14)

        partial = self.oracle(2, 3, False)["applied"]
        self.assertEqual(
            [index + 1 for index, event in enumerate(partial["transfer"]) if event],
            [1, 4, 8, 11, 14, 17, 20, 23],
        )
        self.assertEqual(
            [index + 1 for index, event in enumerate(partial["neither"]) if event],
            [5, 6],
        )
        self.assertEqual(
            [index + 1 for index, event in enumerate(partial["stalled"]) if event],
            [7],
        )
        self.assertEqual(partial["data"][6], 822)
        self.assertEqual(partial["wait_cycles"], [0, 0, 1, 0, 0, 0, 0, 0])
        self.assertEqual(partial["active_stalls"], 1)
        self.assertEqual(partial["maximum_wait"], 1)
        self.assertEqual(partial["completion"], 23)
        self.assertEqual(partial["active_bubbles"], 14)
        self.assertEqual(partial["accepted_data"], TOKEN_CODES)

    def test_limits_include_early_ready_long_hold_and_final_record_edge(self):
        always = self.oracle(0, 0, False)["applied"]
        self.assertEqual(always["transfer_cycle"], list(range(1, 9)))
        self.assertEqual(always["active_rate"], 1)
        longest = self.oracle(0, 6, False)["applied"]
        self.assertEqual(longest["transfer_cycle"], [1, 2, 3, 4, 11, 12, 13, 14])
        self.assertEqual(longest["data"][4:11], [1644] * 7)
        sparse = self.oracle(3, 0, False)["applied"]
        self.assertEqual(sparse["transfer_cycle"], [1, 5, 9, 13, 17, 21, 25, 29])
        final_edge = self.oracle(3, 6, False)["applied"]
        self.assertTrue(final_edge["completed"])
        self.assertEqual(final_edge["completion"], 35)
        self.assertTrue(final_edge["transfer"][-1])
        self.assertEqual(final_edge["accepted_data"], TOKEN_CODES)

    def test_broken_advance_has_exact_drop_hold_and_sequence_symptom(self):
        healthy = self.oracle(0, 3, False)
        broken = self.oracle(0, 3, True)
        self.assertEqual(broken["reference"], healthy["applied"])
        path = broken["applied"]
        self.assertTrue(broken["fault_active"])
        self.assertEqual(path["accepted_ids"], [1, 2, 3, 4, 8])
        self.assertEqual(path["accepted_data"], [0, 411, 822, 1233, 2877])
        self.assertEqual(path["lost_ids"], [5, 6, 7])
        self.assertEqual(
            [index + 1 for index, event in enumerate(path["drops"]) if event],
            [5, 6, 7],
        )
        self.assertEqual(
            [index + 1 for index, event in enumerate(path["hold_violations"]) if event],
            [6, 7, 8],
        )
        self.assertEqual((path["drop_count"], path["hold_violation_count"]), (3, 3))
        self.assertFalse(path["completed"])
        inert = self.oracle(0, 0, True)
        self.assertFalse(inert["fault_active"])
        self.assertEqual(inert["applied"]["valid"], inert["reference"]["valid"])
        self.assertEqual(inert["applied"]["data"], inert["reference"]["data"])
        self.assertEqual(inert["applied"]["transfer"], inert["reference"]["transfer"])

    def test_complete_control_grid_is_deterministic_isolated_and_resource_bounded(self):
        baseline = self.oracle()
        for gap in range(4):
            for stall in range(7):
                healthy = self.oracle(gap, stall, False)
                broken = self.oracle(gap, stall, True)
                with self.subTest(gap=gap, stall=stall):
                    path = healthy["applied"]
                    self.assertTrue(path["completed"])
                    self.assertLessEqual(path["completion"], 35)
                    self.assertEqual(path["accepted_ids"], list(range(1, 9)))
                    self.assertEqual(path["accepted_data"], TOKEN_CODES)
                    self.assertEqual(path["lost_ids"], [])
                    self.assertFalse(any(path["hold_violations"]))
                    self.assertEqual(broken["reference"], path)
                    broken_path = broken["applied"]
                    self.assertEqual(
                        len(broken_path["accepted_ids"]) + len(broken_path["lost_ids"]),
                        8,
                    )
                    self.assertEqual(broken_path["drop_count"], len(broken_path["lost_ids"]))
                    self.assertEqual(broken_path["record_values"], 35)
                    self.assertEqual(broken_path["token_values"], 8)
                    self.assertEqual(healthy["payload_bits"], 12)
                    self.assertTrue(
                        all(
                            transfer == (valid and ready)
                            for valid, ready, transfer in zip(
                                broken_path["valid"],
                                broken_path["ready"],
                                broken_path["transfer"],
                            )
                        )
                    )
        self.assertEqual(self.oracle(), baseline)

    def test_malformed_inputs_reject_and_valid_call_recovers(self):
        invalid_calls = (
            (-1, 3, False),
            (4, 3, False),
            (1.5, 3, False),
            ([1, 2], 3, False),
            (math.nan, 3, False),
            (math.inf, 3, False),
            (1 + 1j, 3, False),
            (True, 3, False),
            (1, -1, False),
            (1, 7, False),
            (1, 3.5, False),
            (1, [3, 4], False),
            (1, math.nan, False),
            (1, math.inf, False),
            (1, 3 + 1j, False),
            (1, True, False),
            (1, 3, 2),
            (1, 3, 0.5),
            (1, 3, [False, True]),
            (1, 3, math.nan),
            (1, 3, math.inf),
            (1, 3, 1 + 1j),
        )
        expected = self.oracle()
        for arguments in invalid_calls:
            with self.subTest(arguments=arguments):
                with self.assertRaises(ValueError):
                    self.oracle(*arguments)
                self.assertEqual(self.oracle(), expected)
        self.oracle(3, 6, False)
        self.oracle(0, 3, True)
        self.assertEqual(self.oracle(), expected)


if __name__ == "__main__":
    unittest.main()
