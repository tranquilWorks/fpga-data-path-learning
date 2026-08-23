from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_FOLDER = ROOT / "modules/11-frame-packets-across-a-stream"
GUIDING_QUESTION = (
    "What inputs, observable effects, and failure modes matter when you frame "
    "Packets Across a Stream?"
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
PAYLOAD_WORDS = [0, 411, 822, 1233, 1644, 2055, 2466, 2877, 3288, 3699, 14, 425]
ALLOWED_PACKET_LENGTHS = (2, 3, 4, 6)


class P11ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "curriculum/modules.json").read_text(encoding="utf-8")
        )
        cls.module = next(
            module for module in cls.manifest["modules"] if module["id"] == "P11"
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
                "number": 11,
                "id": "P11",
                "title": "Frame Packets Across a Stream",
                "guiding_question": GUIDING_QUESTION,
                "phase": 3,
                "phase_title": "Streaming architectures",
                "slug": "frame-packets-across-a-stream",
                "folder": "modules/11-frame-packets-across-a-stream",
                "implementation_batch": "P11",
                "prerequisites": ["P10"],
                "status": "implemented",
                "evidence_level": "simulated",
            },
        )
        p10 = next(
            module for module in self.manifest["modules"] if module["id"] == "P10"
        )
        self.assertEqual(p10["status"], "implemented")
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
            "p10",
            "valid",
            "ready",
            "payload",
            "last",
            "transfer[n]",
            "packetend[n]",
            "12-bit phase-code labels",
            "whole-beat",
        ):
            self.assertIn(marker, lesson)
        for marker in (
            "learning cycle",
            "visualize the baseline",
            "lever 1",
            "lever 2",
            "mechanism first",
            "deliberately broken case",
            "aliasing limit",
        ):
            self.assertIn(marker, lesson)
        self.assertIn("make no second prediction", lesson)
        self.assertIn("make no second prediction", walkthrough)
        self.assertIn("one prompt at a time", checks)
        self.assertIn("limiting-case checks", checks)
        self.assertIn("interpretation and transfer check", checks)
        self.assertIn("teach-back", checks)
        self.assertIn("two sentences", checks)
        for limitation in (
            "p12 fifo sizing",
            "p18 axi-stream details",
            "crc/fcs",
            "partial-byte qualifiers",
            "cdc safety",
            "synthesis",
            "timeout",
            "cancellation",
            "liveness",
        ):
            self.assertIn(limitation, checks)

    def test_model_is_transparent_deterministic_bounded_and_presentation_free(self):
        source = self.read("model.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        for expression in (
            "allowedPacketLengths=[2346];",
            "payloadAccumulatorBits=12;",
            "payloadTuningWord=411;",
            "beatCount=12;",
            "recordCycleCount=24;",
            "consumerStallStartCycle=4;",
            "maximumConsumerStallCycles=6;",
            "payloadWords=mod((beatOrdinal-1)*payloadTuningWord,payloadModulus);",
            "expectedLastByBeat=mod(beatOrdinal,packetLength)==0;",
            "sourceReady=consumerReady;",
            "transfer(cycleIndex)=sourceValid(cycleIndex)&&sourceReady(cycleIndex);",
            "markerAdvance(cycleIndex)=transfer(cycleIndex)||(brokenMode&&sourceValid(cycleIndex));",
            "boundaryMismatch=acceptedLast~=acceptedExpectedLast;",
        ):
            self.assertIn(expression, compact)
        for field in (
            "reference",
            "applied",
            "sourceValid",
            "sourceReady",
            "sourcePayloadWord",
            "sourceExpectedLast",
            "sourceLast",
            "transfer",
            "sourceStalled",
            "payloadHoldViolation",
            "lastHoldViolation",
            "markerAdvanceWhileStalled",
            "acceptedBeatOrdinals",
            "acceptedPayloadWords",
            "acceptedLast",
            "observedBoundaryBeatOrdinals",
            "completedPacketLengths",
            "trailingBeatCount",
            "boundaryMismatchCount",
            "dataCompleted",
            "framingValid",
            "completionCycle",
            "maxRecordCycles",
            "maxBeatCount",
            "maxPacketCount",
        ):
            self.assertIn(field, source)
        for identifier in (
            "P11:InvalidPacketLength",
            "P11:InvalidConsumerStallCycles",
            "P11:InvalidBrokenAdvanceLast",
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
        compact_model = re.sub(r"\s+", "", self.read("model.m")).replace(
            "...", ""
        )
        for conversion in (
            "packetLength=double(packetLength);",
            "consumerStallCycles=double(consumerStallCycles);",
            "brokenAdvanceLast=logical(brokenAdvanceLast);",
        ):
            self.assertIn(conversion, compact_model)
        compact_checks = re.sub(
            r"\s+", "", self.read("run_checks.m")
        ).replace("...", "")
        self.assertIn(
            "typedBaseline=model(uint8(4),uint8(3),uint8(0));",
            compact_checks,
        )
        self.assertIn("isequaln(typedBaseline,baseline)", compact_checks)
        self.assertIn("P11:NumericClassNormalization", self.read("run_checks.m"))

    def test_experiment_has_independent_sweeps_labels_metrics_and_broken_case(self):
        source = self.read("experiment.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        self.assertGreaterEqual(source.count("%%"), 20)
        self.assertIn("sweep 1", lower)
        self.assertIn("sweep 2", lower)
        self.assertIn("packetLengthSweep=[2346];", compact)
        self.assertIn("consumerStallSweep=0:6;", compact)
        self.assertIn("model(packetLengthSweep(sweepIndex),3,false)", compact)
        self.assertIn("model(4,consumerStallSweep(sweepIndex),false)", compact)
        self.assertIn("packet-length sweep must preserve", lower)
        self.assertIn("consumer-stall sweep must preserve", lower)
        self.assertIn("deliberately broken case", lower)
        self.assertIn("healthy=model(4,3,false);", compact)
        self.assertIn("broken=model(4,3,true);", compact)
        self.assertIn("advance last while payload is stalled", lower)
        self.assertIn("broken.applied.boundarymismatchcount==5", compact.lower())
        self.assertGreaterEqual(lower.count("drawnow"), 16)
        self.assertIn("run one section at a time", lower)
        self.assertGreaterEqual(lower.count("xlabel("), 16)
        self.assertGreaterEqual(lower.count("ylabel("), 16)
        for unit_marker in (
            "[cycles]",
            "[binary, vertically offset]",
            "[beat ordinal from one]",
            "[beats/packet]",
            "[boundaries/beat]",
            "[beats/cycle]",
        ):
            self.assertIn(unit_marker, lower)
        for metric in (
            "completion",
            "accepted",
            "packet",
            "boundary",
            "trailing",
            "hold violation",
        ):
            self.assertIn(metric, lower)
        self.assertNotIn("close all", lower)

    def test_interactive_controls_are_bounded_model_backed_and_fault_safe(self):
        source = self.read("interactive.m")
        lower = source.lower()
        self.assertIn("modelFcn = @model", source)
        self.assertIn("uidropdown(", lower)
        self.assertGreaterEqual(lower.count("uispinner("), 2)
        self.assertIn("uicheckbox(", lower)
        self.assertRegex(source, r"'Items'\s*,\s*\{'2','3','4','6'\}")
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*0\s+6\s*\]")
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*1\s+24\s*\]")
        self.assertGreaterEqual(source.count("ValueChangedFcn"), 4)
        clear_fault = source.index("faultCheckbox.Value = false")
        disable_fault = source.index("faultCheckbox.Enable = 'off'")
        self.assertLess(clear_fault, disable_fault)
        for phrase in (
            "valid && ready && last",
            "packet length",
            "consumer ready-low duration",
            "observation cycle",
            "boundary mismatches",
            "24-cycle trace",
            "not measured throughput",
            "axi-stream compliance claim",
        ):
            self.assertIn(phrase, lower)
        self.assertIn("out.applied.sourceLast", source)
        self.assertIn("out.applied.transfer", source)
        self.assertIn("out.applied.observedBoundaryBeatOrdinals", source)
        self.assertIn("out.applied.completedPacketLengths", source)
        self.assertNotIn("close all", lower)

    def test_checks_cover_equations_limits_fault_validation_recovery_and_bounds(self):
        source = self.read("run_checks.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "").lower()
        self.assertGreaterEqual(lower.count("assert("), 30)
        self.assertIn(
            "expectedpayloadwords=[0411822123316442055246628773288369914425].';",
            compact,
        )
        self.assertIn("packetlengthsweep=[2346];", compact)
        self.assertIn("consumerstallsweep=0:6;", compact)
        self.assertIn("forpacketlength=[2346]", compact)
        self.assertIn("forconsumerstallcycles=0:6", compact)
        self.assertIn("shortpacketsnostall=model(2,0,false);", compact)
        self.assertIn("longpacketslongeststall=model(6,6,false);", compact)
        self.assertIn("inertnostall=model(4,0,true);", compact)
        self.assertIn("aliasedfault=model(4,4,true);", compact)
        for identifier in (
            "P11:BaselineShape",
            "P11:BaselinePacketMap",
            "P11:BaselineTransfers",
            "P11:BaselineFraming",
            "P11:BaselineMetrics",
            "P11:NumericClassNormalization",
            "P11:TransferEquation",
            "P11:HealthyWholeBeatHold",
            "P11:HealthyReference",
            "P11:PacketLengthSweep",
            "P11:PacketLengthSweepIsolation",
            "P11:ConsumerStallSweep",
            "P11:ConsumerStallSweepIsolation",
            "P11:ShortestPacketNoStallLimit",
            "P11:LongestPacketLongestStallLimit",
            "P11:BrokenLastHold",
            "P11:BrokenPayloadIsolation",
            "P11:BrokenFramingSymptom",
            "P11:BrokenInertNoStall",
            "P11:BrokenBoundaryAliasingLimit",
            "P11:NonBoundaryHiddenAdvance",
            "P11:NonBoundaryDelayedCorruption",
            "P11:HealthyGrid",
            "P11:BrokenGrid",
            "P11:ResourceBound",
            "P11:DeterminismRecovery",
            "P11:InvalidPacketLength",
            "P11:InvalidConsumerStallCycles",
            "P11:InvalidBrokenAdvanceLast",
        ):
            self.assertIn(identifier.lower(), lower)
        self.assertIn("p11 checks passed", lower)
        self.assertIn("healthynonboundary=model(3,1,false);", compact)
        self.assertIn("brokennonboundary=model(3,1,true);", compact)

    def test_p11_text_files_have_exactly_one_terminal_newline(self):
        for name in REQUIRED_ARTIFACTS:
            with self.subTest(artifact=name):
                data = (MODULE_FOLDER / name).read_bytes()
                self.assertTrue(data.endswith(b"\n"))
                self.assertFalse(data.endswith(b"\n\n"))
                self.assertNotIn(b"\r", data)


class P11IndependentOracleTests(unittest.TestCase):
    @staticmethod
    def oracle(
        packet_length: int = 4,
        consumer_stall_cycles: int = 3,
        broken_advance_last: bool = False,
    ):
        if type(packet_length) is not int or packet_length not in ALLOWED_PACKET_LENGTHS:
            raise ValueError("packet_length")
        if (
            type(consumer_stall_cycles) is not int
            or not 0 <= consumer_stall_cycles <= 6
        ):
            raise ValueError("consumer_stall_cycles")
        valid_flag = type(broken_advance_last) is bool or (
            type(broken_advance_last) is int and broken_advance_last in (0, 1)
        )
        if not valid_flag:
            raise ValueError("broken_advance_last")
        broken_advance_last = bool(broken_advance_last)

        record_cycles = 24
        beat_count = 12
        consumer_ready = [True] * record_cycles
        for cycle in range(4, 4 + consumer_stall_cycles):
            consumer_ready[cycle - 1] = False
        expected_last_by_beat = [
            beat % packet_length == 0 for beat in range(1, beat_count + 1)
        ]

        def simulate(broken: bool):
            current_payload_beat = 1
            current_marker_beat = 1
            source_valid: list[bool] = []
            source_ready: list[bool] = consumer_ready.copy()
            source_beat: list[int] = []
            source_payload: list[int | None] = []
            source_expected_last: list[bool] = []
            source_last: list[bool] = []
            marker_beat: list[int] = []
            transfer: list[bool] = []
            source_stalled: list[bool] = []
            payload_advance: list[bool] = []
            marker_advance: list[bool] = []
            accepted_beat_by_cycle: list[int] = []
            accepted_payload_by_cycle: list[int | None] = []
            accepted_last_by_cycle: list[bool] = []
            accepted_expected_last_by_cycle: list[bool] = []
            transfer_cycle_by_beat: list[int | None] = [None] * beat_count

            for index in range(record_cycles):
                valid = current_payload_beat <= beat_count
                beat = current_payload_beat if valid else 0
                payload = PAYLOAD_WORDS[beat - 1] if valid else None
                expected_last = expected_last_by_beat[beat - 1] if valid else False
                last = current_marker_beat % packet_length == 0 if valid else False
                moved = valid and source_ready[index]
                stalled = valid and not source_ready[index]
                move_payload = moved
                move_marker = moved or (broken and valid)

                source_valid.append(valid)
                source_beat.append(beat)
                source_payload.append(payload)
                source_expected_last.append(expected_last)
                source_last.append(last)
                marker_beat.append(current_marker_beat if valid else 0)
                transfer.append(moved)
                source_stalled.append(stalled)
                payload_advance.append(move_payload)
                marker_advance.append(move_marker)
                accepted_beat_by_cycle.append(beat if moved else 0)
                accepted_payload_by_cycle.append(payload if moved else None)
                accepted_last_by_cycle.append(last if moved else False)
                accepted_expected_last_by_cycle.append(
                    expected_last if moved else False
                )
                if moved:
                    transfer_cycle_by_beat[beat - 1] = index + 1
                if move_payload:
                    current_payload_beat += 1
                if move_marker:
                    current_marker_beat += 1

            payload_hold_violations = [False] * record_cycles
            last_hold_violations = [False] * record_cycles
            for index in range(1, record_cycles):
                if source_valid[index - 1] and not source_ready[index - 1]:
                    payload_hold_violations[index] = (
                        not source_valid[index]
                        or source_beat[index] != source_beat[index - 1]
                        or source_payload[index] != source_payload[index - 1]
                    )
                    last_hold_violations[index] = (
                        not source_valid[index]
                        or source_last[index] != source_last[index - 1]
                    )

            accepted_beats = [beat for beat, moved in zip(source_beat, transfer) if moved]
            accepted_payloads = [
                payload for payload, moved in zip(source_payload, transfer) if moved
            ]
            accepted_last = [last for last, moved in zip(source_last, transfer) if moved]
            accepted_expected_last = [
                last
                for last, moved in zip(source_expected_last, transfer)
                if moved
            ]
            boundary_positions = [
                index + 1 for index, last in enumerate(accepted_last) if last
            ]
            boundary_beats = [accepted_beats[index - 1] for index in boundary_positions]
            packet_lengths: list[int] = []
            previous = 0
            for position in boundary_positions:
                packet_lengths.append(position - previous)
                previous = position
            trailing = len(accepted_beats) - (boundary_positions[-1] if boundary_positions else 0)
            boundary_mismatch = [
                actual != expected
                for actual, expected in zip(accepted_last, accepted_expected_last)
            ]
            lost = sorted(set(range(1, beat_count + 1)) - set(accepted_beats))
            duplicates = len(accepted_beats) - len(set(accepted_beats))
            out_of_order = sum(
                right <= left for left, right in zip(accepted_beats, accepted_beats[1:])
            )
            data_completed = (
                len(accepted_beats) == beat_count
                and not lost
                and duplicates == 0
                and out_of_order == 0
            )
            completion = (
                max(index + 1 for index, moved in enumerate(transfer) if moved)
                if data_completed
                else None
            )
            expected_packet_count = beat_count // packet_length
            framing_valid = (
                data_completed
                and not any(boundary_mismatch)
                and len(boundary_positions) == expected_packet_count
                and trailing == 0
                and packet_lengths == [packet_length] * expected_packet_count
            )
            marker_while_stalled = [
                advance and stalled
                for advance, stalled in zip(marker_advance, source_stalled)
            ]
            active_window = completion if completion is not None else record_cycles
            return {
                "broken": broken,
                "source_valid": source_valid,
                "source_ready": source_ready,
                "source_beat": source_beat,
                "source_payload": source_payload,
                "source_expected_last": source_expected_last,
                "source_last": source_last,
                "marker_beat": marker_beat,
                "transfer": transfer,
                "source_stalled": source_stalled,
                "payload_advance": payload_advance,
                "marker_advance": marker_advance,
                "marker_while_stalled": marker_while_stalled,
                "accepted_beat_by_cycle": accepted_beat_by_cycle,
                "accepted_payload_by_cycle": accepted_payload_by_cycle,
                "accepted_last_by_cycle": accepted_last_by_cycle,
                "accepted_expected_last_by_cycle": accepted_expected_last_by_cycle,
                "transfer_cycle_by_beat": transfer_cycle_by_beat,
                "payload_hold_violations": payload_hold_violations,
                "last_hold_violations": last_hold_violations,
                "accepted_beats": accepted_beats,
                "accepted_payloads": accepted_payloads,
                "accepted_last": accepted_last,
                "accepted_expected_last": accepted_expected_last,
                "boundary_positions": boundary_positions,
                "boundary_beats": boundary_beats,
                "packet_lengths": packet_lengths,
                "trailing": trailing,
                "boundary_mismatch": boundary_mismatch,
                "boundary_mismatch_count": sum(boundary_mismatch),
                "lost": lost,
                "duplicates": duplicates,
                "out_of_order": out_of_order,
                "data_completed": data_completed,
                "framing_valid": framing_valid,
                "completion": completion,
                "source_stall_count": sum(source_stalled),
                "packet_count": len(boundary_positions),
                "last_hold_violation_count": sum(last_hold_violations),
                "payload_hold_violation_count": sum(payload_hold_violations),
                "marker_while_stalled_count": sum(marker_while_stalled),
                "boundary_density": len(boundary_positions) / len(accepted_beats),
                "active_rate": len(accepted_beats) / active_window,
                "trace_values": len(source_valid),
                "beat_values": len(accepted_beats),
            }

        reference = simulate(False)
        applied = simulate(broken_advance_last)
        fault_active = broken_advance_last and any(applied["marker_while_stalled"])
        frame_fault_visible = broken_advance_last and not applied["framing_valid"]
        return {
            "packet_length": packet_length,
            "consumer_stall_cycles": consumer_stall_cycles,
            "broken": broken_advance_last,
            "consumer_ready": consumer_ready,
            "payload_words": PAYLOAD_WORDS.copy(),
            "expected_last": expected_last_by_beat,
            "expected_boundaries": [
                index + 1 for index, last in enumerate(expected_last_by_beat) if last
            ],
            "expected_packet_count": beat_count // packet_length,
            "reference": reference,
            "applied": applied,
            "fault_active": fault_active,
            "frame_fault_visible": frame_fault_visible,
            "record_cycles": record_cycles,
            "beat_count": beat_count,
            "maximum_packets": 6,
            "payload_bits": 12,
        }

    def test_exact_baseline_transfers_holds_boundaries_and_metrics(self):
        result = self.oracle()
        path = result["applied"]
        self.assertEqual(result["payload_words"], PAYLOAD_WORDS)
        self.assertEqual(
            [index + 1 for index, event in enumerate(path["transfer"]) if event],
            [1, 2, 3] + list(range(7, 16)),
        )
        self.assertEqual(
            [index + 1 for index, event in enumerate(path["source_stalled"]) if event],
            [4, 5, 6],
        )
        self.assertEqual(path["source_beat"][3:7], [4, 4, 4, 4])
        self.assertEqual(path["source_payload"][3:7], [1233] * 4)
        self.assertEqual(path["source_last"][3:7], [True] * 4)
        self.assertEqual(path["accepted_beats"], list(range(1, 13)))
        self.assertEqual(path["accepted_payloads"], PAYLOAD_WORDS)
        self.assertEqual(path["boundary_beats"], [4, 8, 12])
        self.assertEqual(path["packet_lengths"], [4, 4, 4])
        self.assertEqual(path["trailing"], 0)
        self.assertEqual(path["completion"], 15)
        self.assertEqual(path["active_rate"], 12 / 15)
        self.assertEqual(path["boundary_density"], 1 / 4)
        self.assertTrue(path["data_completed"])
        self.assertTrue(path["framing_valid"])
        self.assertEqual(result["reference"], path)

    def test_transfer_packet_end_and_whole_beat_hold_rules(self):
        result = self.oracle()
        path = result["applied"]
        for index in range(result["record_cycles"]):
            self.assertEqual(
                path["transfer"][index],
                path["source_valid"][index] and path["source_ready"][index],
            )
        self.assertFalse(any(path["payload_hold_violations"]))
        self.assertFalse(any(path["last_hold_violations"]))
        self.assertEqual(
            [beat for beat, last in zip(path["accepted_beats"], path["accepted_last"]) if last],
            result["expected_boundaries"],
        )
        self.assertEqual(path["lost"], [])
        self.assertEqual(path["duplicates"], 0)
        self.assertEqual(path["out_of_order"], 0)

    def test_packet_length_sweep_changes_grouping_not_ready_payload_or_timing(self):
        results = [self.oracle(length, 3, False) for length in ALLOWED_PACKET_LENGTHS]
        self.assertEqual(
            [result["applied"]["packet_count"] for result in results],
            [6, 4, 3, 2],
        )
        self.assertEqual(
            [result["applied"]["boundary_density"] for result in results],
            [1 / 2, 1 / 3, 1 / 4, 1 / 6],
        )
        expected_ready = self.oracle()["consumer_ready"]
        expected_transfers = self.oracle()["applied"]["transfer"]
        for length, result in zip(ALLOWED_PACKET_LENGTHS, results):
            path = result["applied"]
            self.assertEqual(result["consumer_ready"], expected_ready)
            self.assertEqual(result["payload_words"], PAYLOAD_WORDS)
            self.assertEqual(path["transfer"], expected_transfers)
            self.assertEqual(path["packet_lengths"], [length] * (12 // length))
            self.assertEqual(path["completion"], 15)
            self.assertTrue(path["data_completed"])
            self.assertTrue(path["framing_valid"])

    def test_consumer_stall_sweep_changes_timing_not_payload_or_boundaries(self):
        results = [self.oracle(4, stall, False) for stall in range(7)]
        self.assertEqual(
            [result["applied"]["completion"] for result in results],
            list(range(12, 19)),
        )
        self.assertEqual(
            [result["applied"]["source_stall_count"] for result in results],
            list(range(7)),
        )
        self.assertEqual(
            [result["applied"]["active_rate"] for result in results],
            [12 / completion for completion in range(12, 19)],
        )
        for result in results:
            path = result["applied"]
            self.assertEqual(result["packet_length"], 4)
            self.assertEqual(path["accepted_payloads"], PAYLOAD_WORDS)
            self.assertEqual(path["boundary_beats"], [4, 8, 12])
            self.assertEqual(path["packet_lengths"], [4, 4, 4])
            self.assertEqual(path["boundary_mismatch_count"], 0)
            self.assertTrue(path["framing_valid"])

    def test_limiting_cases_are_complete_and_bounded(self):
        shortest = self.oracle(2, 0, False)["applied"]
        self.assertEqual(shortest["transfer_cycle_by_beat"], list(range(1, 13)))
        self.assertEqual(shortest["boundary_beats"], list(range(2, 13, 2)))
        self.assertEqual(shortest["packet_lengths"], [2] * 6)
        self.assertEqual(shortest["completion"], 12)
        longest = self.oracle(6, 6, False)["applied"]
        self.assertEqual(longest["boundary_beats"], [6, 12])
        self.assertEqual(longest["packet_lengths"], [6, 6])
        self.assertEqual(longest["source_stall_count"], 6)
        self.assertEqual(longest["completion"], 18)
        self.assertTrue(longest["data_completed"])
        self.assertTrue(longest["framing_valid"])

    def test_broken_advance_last_has_exact_framing_not_payload_symptom(self):
        healthy = self.oracle(4, 3, False)
        broken = self.oracle(4, 3, True)
        path = broken["applied"]
        self.assertEqual(broken["reference"], healthy["applied"])
        self.assertTrue(broken["fault_active"])
        self.assertTrue(broken["frame_fault_visible"])
        self.assertEqual(path["marker_while_stalled_count"], 3)
        self.assertEqual(
            [index + 1 for index, event in enumerate(path["last_hold_violations"]) if event],
            [5],
        )
        self.assertEqual(path["payload_hold_violation_count"], 0)
        self.assertEqual(path["accepted_beats"], list(range(1, 13)))
        self.assertEqual(path["accepted_payloads"], PAYLOAD_WORDS)
        self.assertEqual(path["lost"], [])
        self.assertEqual(path["duplicates"], 0)
        self.assertEqual(path["out_of_order"], 0)
        self.assertEqual(path["boundary_beats"], [5, 9])
        self.assertEqual(path["packet_lengths"], [5, 4])
        self.assertEqual(path["trailing"], 3)
        self.assertEqual(path["boundary_mismatch_count"], 5)
        self.assertEqual(
            [index + 1 for index, event in enumerate(path["boundary_mismatch"]) if event],
            [4, 5, 8, 9, 12],
        )
        self.assertTrue(path["data_completed"])
        self.assertFalse(path["framing_valid"])
        self.assertEqual(path["completion"], healthy["applied"]["completion"])

    def test_fault_inert_without_stall_and_whole_packet_drift_aliases(self):
        inert = self.oracle(4, 0, True)
        healthy = self.oracle(4, 0, False)
        self.assertFalse(inert["fault_active"])
        self.assertFalse(inert["frame_fault_visible"])
        inert_path = dict(inert["applied"])
        healthy_path = dict(healthy["applied"])
        inert_path.pop("broken")
        healthy_path.pop("broken")
        self.assertEqual(inert_path, healthy_path)

        aliased = self.oracle(4, 4, True)
        path = aliased["applied"]
        self.assertTrue(aliased["fault_active"])
        self.assertFalse(aliased["frame_fault_visible"])
        self.assertEqual(path["marker_while_stalled_count"], 4)
        self.assertGreater(path["last_hold_violation_count"], 0)
        self.assertEqual(path["boundary_beats"], [4, 8, 12])
        self.assertEqual(path["packet_lengths"], [4, 4, 4])
        self.assertTrue(path["framing_valid"])

    def test_nonboundary_stall_hides_last_toggle_then_corrupts_future_frames(self):
        healthy = self.oracle(3, 1, False)
        broken = self.oracle(3, 1, True)
        path = broken["applied"]
        self.assertEqual(broken["reference"], healthy["applied"])
        self.assertEqual(healthy["applied"]["boundary_beats"], [3, 6, 9, 12])
        self.assertEqual(
            [index + 1 for index, event in enumerate(path["source_stalled"]) if event],
            [4],
        )
        self.assertEqual(path["source_beat"][3:5], [4, 4])
        self.assertEqual(path["marker_beat"][3:5], [4, 5])
        self.assertEqual(path["source_last"][3:5], [False, False])
        self.assertEqual(path["marker_while_stalled_count"], 1)
        self.assertEqual(path["last_hold_violation_count"], 0)
        self.assertTrue(broken["fault_active"])
        self.assertTrue(broken["frame_fault_visible"])
        self.assertEqual(path["accepted_beats"], list(range(1, 13)))
        self.assertEqual(path["accepted_payloads"], PAYLOAD_WORDS)
        self.assertEqual(path["payload_hold_violation_count"], 0)
        self.assertTrue(path["data_completed"])
        self.assertEqual(path["completion"], 13)
        self.assertEqual(path["boundary_beats"], [3, 5, 8, 11])
        self.assertEqual(path["packet_lengths"], [3, 2, 3, 3])
        self.assertEqual(path["trailing"], 1)
        self.assertEqual(path["boundary_mismatch_count"], 6)
        self.assertEqual(
            [index + 1 for index, event in enumerate(path["boundary_mismatch"]) if event],
            [5, 6, 8, 9, 11, 12],
        )
        self.assertFalse(path["framing_valid"])

    def test_complete_control_grid_is_deterministic_isolated_and_resource_bounded(self):
        baseline = self.oracle()
        for length in ALLOWED_PACKET_LENGTHS:
            for stall in range(7):
                healthy = self.oracle(length, stall, False)
                healthy_again = self.oracle(length, stall, False)
                broken = self.oracle(length, stall, True)
                with self.subTest(length=length, stall=stall):
                    self.assertEqual(healthy, healthy_again)
                    path = healthy["applied"]
                    self.assertTrue(path["data_completed"])
                    self.assertTrue(path["framing_valid"])
                    self.assertEqual(path["completion"], 12 + stall)
                    self.assertEqual(path["accepted_beats"], list(range(1, 13)))
                    self.assertEqual(path["accepted_payloads"], PAYLOAD_WORDS)
                    self.assertEqual(path["lost"], [])
                    self.assertEqual(path["duplicates"], 0)
                    self.assertEqual(path["out_of_order"], 0)
                    self.assertEqual(path["payload_hold_violation_count"], 0)
                    self.assertEqual(path["last_hold_violation_count"], 0)
                    self.assertEqual(broken["reference"], path)
                    broken_path = broken["applied"]
                    self.assertTrue(broken_path["data_completed"])
                    self.assertEqual(broken_path["accepted_beats"], list(range(1, 13)))
                    self.assertEqual(broken_path["accepted_payloads"], PAYLOAD_WORDS)
                    self.assertEqual(broken_path["payload_hold_violation_count"], 0)
                    self.assertEqual(broken["fault_active"], stall > 0)
                    self.assertEqual(
                        broken["frame_fault_visible"], stall % length != 0
                    )
                    self.assertEqual(path["trace_values"], 24)
                    self.assertEqual(path["beat_values"], 12)
                    self.assertEqual(healthy["record_cycles"], 24)
                    self.assertEqual(healthy["beat_count"], 12)
                    self.assertEqual(healthy["maximum_packets"], 6)
                    self.assertEqual(healthy["payload_bits"], 12)
                    self.assertLessEqual(path["completion"], 18)
        self.assertNotEqual(self.oracle(6, 6, False), baseline)
        self.assertNotEqual(self.oracle(4, 3, True), baseline)
        self.assertEqual(self.oracle(), baseline)

    def test_malformed_inputs_reject_and_valid_call_recovers(self):
        baseline = self.oracle()
        malformed = [
            ((1, 3, False), "packet_length"),
            ((5, 3, False), "packet_length"),
            ((2.5, 3, False), "packet_length"),
            (([2, 4], 3, False), "packet_length"),
            ((True, 3, False), "packet_length"),
            ((4, -1, False), "consumer_stall_cycles"),
            ((4, 7, False), "consumer_stall_cycles"),
            ((4, 2.5, False), "consumer_stall_cycles"),
            ((4, [2, 3], False), "consumer_stall_cycles"),
            ((4, True, False), "consumer_stall_cycles"),
            ((4, 3, 2), "broken_advance_last"),
            ((4, 3, 0.5), "broken_advance_last"),
            ((4, 3, [False, True]), "broken_advance_last"),
        ]
        for args, marker in malformed:
            with self.subTest(args=args):
                with self.assertRaisesRegex(ValueError, marker):
                    self.oracle(*args)
                self.assertEqual(self.oracle(), baseline)
        for nonfinite in (math.nan, math.inf, -math.inf):
            with self.subTest(nonfinite=nonfinite, control="packet_length"):
                with self.assertRaisesRegex(ValueError, "packet_length"):
                    self.oracle(nonfinite, 3, False)
                self.assertEqual(self.oracle(), baseline)
            with self.subTest(nonfinite=nonfinite, control="consumer_stall"):
                with self.assertRaisesRegex(ValueError, "consumer_stall_cycles"):
                    self.oracle(4, nonfinite, False)
                self.assertEqual(self.oracle(), baseline)
            with self.subTest(nonfinite=nonfinite, control="fault"):
                with self.assertRaisesRegex(ValueError, "broken_advance_last"):
                    self.oracle(4, 3, nonfinite)
                self.assertEqual(self.oracle(), baseline)
        for complex_value in (4 + 1j, 3 + 1j, 1 + 1j):
            with self.subTest(complex_value=complex_value):
                if complex_value.real == 4:
                    args = (complex_value, 3, False)
                    marker = "packet_length"
                elif complex_value.real == 3:
                    args = (4, complex_value, False)
                    marker = "consumer_stall_cycles"
                else:
                    args = (4, 3, complex_value)
                    marker = "broken_advance_last"
                with self.assertRaisesRegex(ValueError, marker):
                    self.oracle(*args)
                self.assertEqual(self.oracle(), baseline)
        self.assertEqual(self.oracle(4, 3, 0), baseline)
        self.assertEqual(self.oracle(4, 3, 1), self.oracle(4, 3, True))


if __name__ == "__main__":
    unittest.main()
