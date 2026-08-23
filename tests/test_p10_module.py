from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_FOLDER = ROOT / "modules/10-apply-backpressure-without-losing-data"
GUIDING_QUESTION = (
    "What inputs, observable effects, and failure modes matter when you apply "
    "Backpressure Without Losing Data?"
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
TOKEN_CODES = [0, 411, 822, 1233, 1644, 2055, 2466, 2877, 3288, 3699, 14, 425]


class P10ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "curriculum/modules.json").read_text(encoding="utf-8")
        )
        cls.module = next(
            module for module in cls.manifest["modules"] if module["id"] == "P10"
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
                "number": 10,
                "id": "P10",
                "title": "Apply Backpressure Without Losing Data",
                "guiding_question": GUIDING_QUESTION,
                "phase": 3,
                "phase_title": "Streaming architectures",
                "slug": "apply-backpressure-without-losing-data",
                "folder": "modules/10-apply-backpressure-without-losing-data",
                "implementation_batch": "P10",
                "prerequisites": ["P09"],
                "status": "implemented",
                "evidence_level": "simulated",
            },
        )
        p09 = next(
            module for module in self.manifest["modules"] if module["id"] == "P09"
        )
        self.assertEqual(p09["status"], "implemented")
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
            "p09",
            "sourcevalid",
            "sourceready",
            "outputvalid",
            "consumerready",
            "enqueue[n]",
            "dequeue[n]",
            "q[n+1]",
            "registered",
            "12-bit phase-code labels",
        ):
            self.assertIn(marker, lesson)
        for marker in (
            "learning cycle",
            "visualize the baseline",
            "lever 1",
            "lever 2",
            "mechanism first",
            "deliberately broken case",
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
            "free-running source",
            "p11 packet framing",
            "p12 burst/rate fifo sizing",
            "cdc safety",
            "synthesis",
            "deadlock/liveness evidence",
        ):
            self.assertIn(limitation, checks)

    def test_model_is_transparent_deterministic_bounded_and_presentation_free(self):
        source = self.read("model.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        for expression in (
            "payloadAccumulatorBits=12;",
            "payloadTuningWord=411;",
            "tokenCount=12;",
            "recordCycleCount=24;",
            "maximumFifoDepth=6;",
            "consumerStallStartCycle=5;",
            "tokenCodes=mod(tokenOrdinal*payloadTuningWord,payloadModulus);",
            "sourceReady(cycleIndex)=queueCount<fifoDepth||dequeue(cycleIndex);",
            "enqueue(cycleIndex)=sourceValid(cycleIndex)&&sourceReady(cycleIndex);",
            "dropAttempt(cycleIndex)=sourcePaused(cycleIndex)&&brokenMode;",
            "occupancyAfter(cycleIndex)=queueCount;",
            "recurrenceResidual=occupancyAfter-occupancyBefore-double(enqueue)+double(dequeue);",
        ):
            self.assertIn(expression, compact)
        for field in (
            "reference",
            "applied",
            "occupancyBefore",
            "occupancyAfter",
            "sourceValid",
            "sourceReady",
            "enqueue",
            "outputValid",
            "consumerReady",
            "dequeue",
            "sourceHoldViolation",
            "outputHoldViolation",
            "enqueuedTokenIndices",
            "dequeuedTokenIndices",
            "lostTokenCount",
            "duplicateTokenCount",
            "outOfOrderCount",
            "completionCycle",
            "peakOccupancyTokens",
            "finalConservationResidual",
            "maxRecordCycles",
            "maxTokenCount",
            "maxFifoStorageSlots",
        ):
            self.assertIn(field, source)
        for identifier in (
            "P10:InvalidFifoDepth",
            "P10:InvalidConsumerStallCycles",
            "P10:InvalidBrokenIgnoreBackpressure",
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
            "fifoDepth=double(fifoDepth);",
            "consumerStallCycles=double(consumerStallCycles);",
            "brokenIgnoreBackpressure=logical(brokenIgnoreBackpressure);",
        ):
            self.assertIn(conversion, compact_model)
        compact_checks = re.sub(
            r"\s+", "", self.read("run_checks.m")
        ).replace("...", "")
        self.assertIn(
            "typedBaseline=model(uint8(3),uint8(5),uint8(0));",
            compact_checks,
        )
        self.assertIn("isequaln(typedBaseline,baseline)", compact_checks)
        self.assertIn("P10:NumericClassNormalization", self.read("run_checks.m"))

    def test_experiment_has_independent_sweeps_labels_metrics_and_broken_case(self):
        source = self.read("experiment.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        self.assertGreaterEqual(source.count("%%"), 20)
        self.assertIn("sweep 1", lower)
        self.assertIn("sweep 2", lower)
        self.assertIn("consumerStallSweep=0:8;", compact)
        self.assertIn("fifoDepthSweep=1:6;", compact)
        self.assertIn("model(3,consumerStallSweep(sweepIndex),false)", compact)
        self.assertIn("model(fifoDepthSweep(sweepIndex),5,false)", compact)
        self.assertIn("consumer-stall sweep must preserve", lower)
        self.assertIn("fifo-depth sweep must preserve", lower)
        self.assertIn("deliberately broken case", lower)
        self.assertIn("healthy=model(3,5,false);", compact)
        self.assertIn("broken=model(3,5,true);", compact)
        self.assertIn("producer advances while fifo ready is low", lower)
        self.assertIn("broken.applied.dropcount==3", compact.lower())
        self.assertGreaterEqual(lower.count("drawnow"), 16)
        self.assertIn("run one section at a time", lower)
        self.assertGreaterEqual(lower.count("xlabel("), 16)
        self.assertGreaterEqual(lower.count("ylabel("), 16)
        for unit_marker in (
            "[cycles]",
            "[binary, vertically offset]",
            "[tokens]",
            "[clock cycle]",
            "[token index from one]",
        ):
            self.assertIn(unit_marker, lower)
        for metric in (
            "completion",
            "source stalls",
            "peak occupancy",
            "delivered",
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
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*1\s+6\s*\]")
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*0\s+8\s*\]")
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*1\s+24\s*\]")
        self.assertGreaterEqual(source.count("ValueChangedFcn"), 4)
        self.assertIn("healthyProbe.reference.sourceStallCycleCount == 0", source)
        clear_fault = source.index("faultCheckbox.Value = false")
        disable_fault = source.index("faultCheckbox.Enable = 'off'")
        self.assertLess(clear_fault, disable_fault)
        for phrase in (
            "valid && ready",
            "fifo depth",
            "consumer ready-low duration",
            "occupancy before/after",
            "delivered/lost/drops",
            "24-cycle trace",
            "not synthesized storage",
        ):
            self.assertIn(phrase, lower)
        self.assertIn("out.reference.occupancyAfter", source)
        self.assertIn("out.applied.occupancyAfter", source)
        self.assertIn("out.applied.enqueue", source)
        self.assertIn("out.applied.dequeue", source)
        self.assertNotIn("close all", lower)

    def test_checks_cover_equations_limits_fault_validation_recovery_and_bounds(self):
        source = self.read("run_checks.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "").lower()
        self.assertGreaterEqual(lower.count("assert("), 30)
        self.assertIn(
            "expectedtokencodes=[0411822123316442055246628773288369914425].';",
            compact,
        )
        self.assertIn("consumerstallsweep=0:8;", compact)
        self.assertIn("fifodepthsweep=1:6;", compact)
        self.assertIn("forfifodepth=1:6", compact)
        self.assertIn("forconsumerstallcycles=0:8", compact)
        self.assertIn("capacityabsorbs=model(4,3,false);", compact)
        self.assertIn("capacityabsorbsfault=model(4,3,true);", compact)
        self.assertIn("backpressurepropagates=model(4,4,false);", compact)
        self.assertIn("backpressurepropagatesfault=model(4,4,true);", compact)
        for inert_comparison in (
            "rmfield(capacityabsorbsfault.applied,'brokenmode')",
            "rmfield(capacityabsorbs.applied,'brokenmode')",
            "rmfield(inertnostall.applied,'brokenmode')",
            "rmfield(healthynostall.applied,'brokenmode')",
            "rmfield(inertdeep.applied,'brokenmode')",
            "rmfield(healthydeep.applied,'brokenmode')",
        ):
            self.assertIn(inert_comparison, compact)
        for identifier in (
            "P10:BaselineSignals",
            "P10:BaselineTokenAccounting",
            "P10:NumericClassNormalization",
            "P10:HandshakeEquations",
            "P10:OccupancyRecurrence",
            "P10:HealthyHoldRules",
            "P10:HealthyConservation",
            "P10:RegisteredNoFallThrough",
            "P10:FullReplacementLimit",
            "P10:ConsumerStallSweep",
            "P10:ConsumerStallSweepIsolation",
            "P10:FifoDepthSweep",
            "P10:FifoDepthSweepIsolation",
            "P10:CombinedCapacityAbsorbs",
            "P10:CombinedBackpressurePropagates",
            "P10:CombinedFaultBoundary",
            "P10:DepthOneNoStallLimit",
            "P10:DepthOneLongestStallLimit",
            "P10:NoBackpressureLimit",
            "P10:MaximumControlLimit",
            "P10:BrokenIgnoredBackpressure",
            "P10:BrokenReferenceIsolation",
            "P10:BrokenStorageBound",
            "P10:BrokenInertLimit",
            "P10:HealthyGrid",
            "P10:BrokenGrid",
            "P10:ResourceBound",
            "P10:DeterminismRecovery",
            "P10:InvalidFifoDepth",
            "P10:InvalidConsumerStallCycles",
            "P10:InvalidBrokenIgnoreBackpressure",
        ):
            self.assertIn(identifier.lower(), lower)
        self.assertIn("p10 checks passed", lower)

    def test_p10_text_files_have_exactly_one_terminal_newline(self):
        for name in REQUIRED_ARTIFACTS:
            with self.subTest(artifact=name):
                data = (MODULE_FOLDER / name).read_bytes()
                self.assertTrue(data.endswith(b"\n"))
                self.assertFalse(data.endswith(b"\n\n"))
                self.assertNotIn(b"\r", data)


class P10IndependentOracleTests(unittest.TestCase):
    @staticmethod
    def oracle(
        fifo_depth: int = 3,
        consumer_stall_cycles: int = 5,
        broken_ignore_backpressure: bool = False,
    ):
        if type(fifo_depth) is not int or not 1 <= fifo_depth <= 6:
            raise ValueError("fifo_depth")
        if (
            type(consumer_stall_cycles) is not int
            or not 0 <= consumer_stall_cycles <= 8
        ):
            raise ValueError("consumer_stall_cycles")
        valid_flag = type(broken_ignore_backpressure) is bool or (
            type(broken_ignore_backpressure) is int
            and broken_ignore_backpressure in (0, 1)
        )
        if not valid_flag:
            raise ValueError("broken_ignore_backpressure")
        broken_ignore_backpressure = bool(broken_ignore_backpressure)

        record_cycles = 24
        token_count = 12
        consumer_ready = [True] * record_cycles
        for cycle in range(5, 5 + consumer_stall_cycles):
            consumer_ready[cycle - 1] = False

        def simulate(broken: bool):
            queue: list[int] = []
            current_source_id = 1
            occupancy_before: list[int] = []
            occupancy_after: list[int] = []
            source_valid: list[bool] = []
            source_ready: list[bool] = []
            source_id: list[int] = []
            source_code: list[int | None] = []
            enqueue: list[bool] = []
            source_advance: list[bool] = []
            source_paused: list[bool] = []
            drops: list[bool] = []
            output_valid: list[bool] = []
            output_id: list[int] = []
            output_code: list[int | None] = []
            dequeue: list[bool] = []
            dequeued_id_by_cycle: list[int] = []
            dequeued_code_by_cycle: list[int | None] = []
            first_offer: list[int | None] = [None] * token_count
            enqueue_cycle: list[int | None] = [None] * token_count
            dequeue_cycle: list[int | None] = [None] * token_count

            for index in range(record_cycles):
                occupancy_before.append(len(queue))
                current_output_valid = bool(queue)
                current_output_id = queue[0] if queue else 0
                current_output_code = (
                    TOKEN_CODES[current_output_id - 1]
                    if current_output_id
                    else None
                )
                current_dequeue = current_output_valid and consumer_ready[index]

                current_valid = current_source_id <= token_count
                current_source_code = (
                    TOKEN_CODES[current_source_id - 1] if current_valid else None
                )
                if current_valid and first_offer[current_source_id - 1] is None:
                    first_offer[current_source_id - 1] = index + 1
                current_ready = len(queue) < fifo_depth or current_dequeue
                current_enqueue = current_valid and current_ready
                current_paused = current_valid and not current_ready
                current_drop = current_paused and broken

                if current_dequeue:
                    dequeued_id = queue.pop(0)
                    dequeued_id_by_cycle.append(dequeued_id)
                    dequeued_code_by_cycle.append(TOKEN_CODES[dequeued_id - 1])
                    dequeue_cycle[dequeued_id - 1] = index + 1
                else:
                    dequeued_id_by_cycle.append(0)
                    dequeued_code_by_cycle.append(None)

                if current_enqueue:
                    queue.append(current_source_id)
                    enqueue_cycle[current_source_id - 1] = index + 1

                current_advance = current_enqueue or (broken and current_valid)

                source_valid.append(current_valid)
                source_ready.append(current_ready)
                source_id.append(current_source_id if current_valid else 0)
                source_code.append(current_source_code)
                enqueue.append(current_enqueue)
                source_advance.append(current_advance)
                source_paused.append(current_paused)
                drops.append(current_drop)
                output_valid.append(current_output_valid)
                output_id.append(current_output_id)
                output_code.append(current_output_code)
                dequeue.append(current_dequeue)
                occupancy_after.append(len(queue))

                if current_advance:
                    current_source_id += 1

            source_hold_violations = [False] * record_cycles
            output_hold_violations = [False] * record_cycles
            for index in range(1, record_cycles):
                if source_valid[index - 1] and not source_ready[index - 1]:
                    source_hold_violations[index] = not (
                        source_valid[index]
                        and source_id[index] == source_id[index - 1]
                        and source_code[index] == source_code[index - 1]
                    )
                if output_valid[index - 1] and not consumer_ready[index - 1]:
                    output_hold_violations[index] = not (
                        output_valid[index]
                        and output_id[index] == output_id[index - 1]
                        and output_code[index] == output_code[index - 1]
                    )

            enqueued_ids = [token for token, event in zip(source_id, enqueue) if event]
            dequeued_ids = [token for token in dequeued_id_by_cycle if token]
            enqueued_codes = [TOKEN_CODES[token - 1] for token in enqueued_ids]
            dequeued_codes = [TOKEN_CODES[token - 1] for token in dequeued_ids]
            lost_ids = [
                token
                for token in range(1, token_count + 1)
                if token not in dequeued_ids
            ]
            completed = dequeued_ids == list(range(1, token_count + 1)) and not queue
            completion = (
                max(index + 1 for index, event in enumerate(dequeue) if event)
                if completed
                else None
            )
            drain = (
                max(index + 1 for index, event in enumerate(dequeue) if event)
                if any(dequeue)
                else None
            )
            source_wait = [
                None if accepted is None else accepted - offered
                for offered, accepted in zip(first_offer, enqueue_cycle)
            ]
            residence = [
                None
                if stored is None or delivered is None
                else delivered - stored
                for stored, delivered in zip(enqueue_cycle, dequeue_cycle)
            ]
            observed_wait = [value for value in source_wait if value is not None]
            observed_residence = [value for value in residence if value is not None]
            full_replacement = [
                before == fifo_depth and put and take
                for before, put, take in zip(
                    occupancy_before, enqueue, dequeue
                )
            ]
            recurrence = [
                after - before - int(put) + int(take)
                for before, after, put, take in zip(
                    occupancy_before, occupancy_after, enqueue, dequeue
                )
            ]
            return {
                "occupancy_before": occupancy_before,
                "occupancy_after": occupancy_after,
                "source_valid": source_valid,
                "source_ready": source_ready,
                "source_id": source_id,
                "source_code": source_code,
                "enqueue": enqueue,
                "source_advance": source_advance,
                "source_paused": source_paused,
                "drops": drops,
                "source_hold_violations": source_hold_violations,
                "output_valid": output_valid,
                "output_id": output_id,
                "output_code": output_code,
                "dequeue": dequeue,
                "dequeued_id_by_cycle": dequeued_id_by_cycle,
                "dequeued_code_by_cycle": dequeued_code_by_cycle,
                "output_hold_violations": output_hold_violations,
                "enqueued_ids": enqueued_ids,
                "enqueued_codes": enqueued_codes,
                "dequeued_ids": dequeued_ids,
                "dequeued_codes": dequeued_codes,
                "first_offer": first_offer,
                "enqueue_cycle": enqueue_cycle,
                "dequeue_cycle": dequeue_cycle,
                "source_wait": source_wait,
                "residence": residence,
                "lost_ids": lost_ids,
                "completed": completed,
                "completion": completion,
                "drain": drain,
                "peak": max(occupancy_after),
                "source_stall_count": sum(source_paused),
                "drop_count": sum(drops),
                "source_hold_violation_count": sum(source_hold_violations),
                "output_hold_violation_count": sum(output_hold_violations),
                "maximum_source_wait": max(observed_wait),
                "maximum_residence": max(observed_residence),
                "minimum_residence": min(observed_residence),
                "full_replacement": full_replacement,
                "recurrence": recurrence,
                "final_conservation": sum(enqueue) - sum(dequeue) - len(queue),
                "final_queue": queue.copy(),
                "record_values": len(occupancy_before),
                "token_values": len(TOKEN_CODES),
            }

        reference = simulate(False)
        applied = simulate(broken_ignore_backpressure)
        return {
            "fifo_depth": fifo_depth,
            "consumer_stall_cycles": consumer_stall_cycles,
            "broken": broken_ignore_backpressure,
            "consumer_ready": consumer_ready,
            "token_codes": TOKEN_CODES.copy(),
            "reference": reference,
            "applied": applied,
            "fault_active": broken_ignore_backpressure
            and bool(applied["drop_count"]),
            "record_cycles": record_cycles,
            "token_count": token_count,
            "maximum_depth": 6,
            "payload_bits": 12,
        }

    def test_exact_baseline_handshakes_occupancy_order_and_metrics(self):
        result = self.oracle()
        path = result["applied"]
        self.assertEqual(result["token_codes"], TOKEN_CODES)
        self.assertEqual(
            [index + 1 for index, event in enumerate(path["enqueue"]) if event],
            [1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15],
        )
        self.assertEqual(
            [index + 1 for index, event in enumerate(path["dequeue"]) if event],
            [2, 3, 4, 10, 11, 12, 13, 14, 15, 16, 17, 18],
        )
        self.assertEqual(
            [index + 1 for index, event in enumerate(path["source_paused"]) if event],
            [7, 8, 9],
        )
        self.assertEqual(
            path["occupancy_before"],
            [0, 1, 1, 1, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 1]
            + [0] * 6,
        )
        self.assertEqual(path["enqueued_ids"], list(range(1, 13)))
        self.assertEqual(path["dequeued_ids"], list(range(1, 13)))
        self.assertEqual(path["enqueued_codes"], TOKEN_CODES)
        self.assertEqual(path["dequeued_codes"], TOKEN_CODES)
        self.assertEqual(path["completion"], 18)
        self.assertEqual(path["peak"], 3)
        self.assertEqual(path["maximum_source_wait"], 3)
        self.assertEqual(path["maximum_residence"], 6)
        self.assertEqual(path["minimum_residence"], 1)
        self.assertEqual(path["lost_ids"], [])
        self.assertEqual(result["reference"], path)

    def test_edge_equations_stable_holds_replacement_and_registered_limit(self):
        result = self.oracle()
        path = result["applied"]
        for index in range(result["record_cycles"]):
            self.assertEqual(
                path["output_valid"][index],
                path["occupancy_before"][index] > 0,
            )
            self.assertEqual(
                path["dequeue"][index],
                path["output_valid"][index] and result["consumer_ready"][index],
            )
            self.assertEqual(
                path["source_ready"][index],
                path["occupancy_before"][index] < result["fifo_depth"]
                or path["dequeue"][index],
            )
            self.assertEqual(
                path["enqueue"][index],
                path["source_valid"][index] and path["source_ready"][index],
            )
            self.assertEqual(path["recurrence"][index], 0)
            self.assertLessEqual(path["occupancy_after"][index], result["fifo_depth"])
            self.assertGreaterEqual(path["occupancy_after"][index], 0)
        self.assertFalse(any(path["source_hold_violations"]))
        self.assertFalse(any(path["output_hold_violations"]))
        self.assertEqual(path["output_id"][4:10], [4] * 6)
        self.assertEqual(path["output_code"][4:10], [1233] * 6)
        self.assertEqual(path["source_id"][6:10], [7] * 4)
        self.assertEqual(path["source_code"][6:10], [2466] * 4)
        self.assertEqual(
            [index + 1 for index, event in enumerate(path["full_replacement"]) if event],
            [10, 11, 12, 13, 14, 15],
        )
        self.assertFalse(path["output_valid"][0])
        self.assertEqual(path["enqueue_cycle"][0], 1)
        self.assertEqual(path["dequeue_cycle"][0], 2)
        self.assertEqual(path["final_conservation"], 0)
        self.assertEqual(path["final_queue"], [])

    def test_consumer_stall_sweep_changes_timing_not_depth_payload_or_order(self):
        results = [self.oracle(3, stall, False) for stall in range(9)]
        self.assertEqual(
            [result["applied"]["completion"] for result in results],
            list(range(13, 22)),
        )
        self.assertEqual(
            [result["applied"]["source_stall_count"] for result in results],
            [0, 0, 0, 1, 2, 3, 4, 5, 6],
        )
        self.assertEqual(
            [result["applied"]["peak"] for result in results],
            [1, 2, 3, 3, 3, 3, 3, 3, 3],
        )
        for result in results:
            path = result["applied"]
            self.assertEqual(result["fifo_depth"], 3)
            self.assertEqual(result["token_codes"], TOKEN_CODES)
            self.assertEqual(path["dequeued_ids"], list(range(1, 13)))
            self.assertEqual(path["dequeued_codes"], TOKEN_CODES)
            self.assertEqual(path["lost_ids"], [])
            self.assertEqual(path["final_conservation"], 0)
            self.assertEqual(path["record_values"], 24)

    def test_fifo_depth_sweep_changes_pause_not_ready_payload_order_or_completion(self):
        results = [self.oracle(depth, 5, False) for depth in range(1, 7)]
        self.assertEqual(
            [result["applied"]["source_stall_count"] for result in results],
            [5, 4, 3, 2, 1, 0],
        )
        self.assertEqual(
            [result["applied"]["peak"] for result in results],
            list(range(1, 7)),
        )
        self.assertEqual(
            [result["applied"]["completion"] for result in results],
            [18] * 6,
        )
        expected_ready = self.oracle(3, 5, False)["consumer_ready"]
        for result in results:
            path = result["applied"]
            self.assertEqual(result["consumer_ready"], expected_ready)
            self.assertEqual(result["token_codes"], TOKEN_CODES)
            self.assertEqual(path["dequeued_ids"], list(range(1, 13)))
            self.assertEqual(path["dequeued_codes"], TOKEN_CODES)
            self.assertEqual(path["lost_ids"], [])
            self.assertEqual(path["final_conservation"], 0)

    def test_combined_capacity_stall_boundary_absorbs_then_propagates(self):
        absorbed = self.oracle(4, 3, False)
        absorbed_path = absorbed["applied"]
        self.assertEqual(
            [
                index + 1
                for index, event in enumerate(absorbed_path["source_paused"])
                if event
            ],
            [],
        )
        self.assertEqual(absorbed_path["enqueue_cycle"], list(range(1, 13)))
        self.assertEqual(
            absorbed_path["dequeue_cycle"],
            [2, 3, 4, 8, 9, 10, 11, 12, 13, 14, 15, 16],
        )
        self.assertEqual(absorbed_path["peak"], 4)
        self.assertEqual(absorbed_path["completion"], 16)
        absorbed_fault = self.oracle(4, 3, True)
        self.assertFalse(absorbed_fault["fault_active"])
        self.assertEqual(absorbed_fault["applied"], absorbed_path)

        propagated = self.oracle(4, 4, False)
        propagated_path = propagated["applied"]
        self.assertEqual(
            [
                index + 1
                for index, event in enumerate(propagated_path["source_paused"])
                if event
            ],
            [8],
        )
        self.assertEqual(propagated_path["source_id"][7:9], [8, 8])
        self.assertEqual(propagated_path["maximum_source_wait"], 1)
        self.assertEqual(propagated_path["peak"], 4)
        self.assertEqual(propagated_path["completion"], 17)
        self.assertEqual(propagated_path["dequeued_ids"], list(range(1, 13)))

        propagated_fault = self.oracle(4, 4, True)
        fault_path = propagated_fault["applied"]
        self.assertTrue(propagated_fault["fault_active"])
        self.assertEqual(propagated_fault["reference"], propagated_path)
        self.assertEqual(
            [index + 1 for index, event in enumerate(fault_path["drops"]) if event],
            [8],
        )
        self.assertEqual(
            [
                index + 1
                for index, event in enumerate(fault_path["source_hold_violations"])
                if event
            ],
            [9],
        )
        self.assertEqual(fault_path["lost_ids"], [8])
        self.assertEqual(
            fault_path["dequeued_ids"],
            [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12],
        )
        self.assertEqual(fault_path["drop_count"], 1)
        self.assertEqual(fault_path["peak"], 4)
        self.assertFalse(fault_path["completed"])

    def test_limiting_cases_are_ordered_lossless_and_bounded(self):
        depth_one_no_stall = self.oracle(1, 0, False)["applied"]
        self.assertEqual(depth_one_no_stall["enqueue_cycle"], list(range(1, 13)))
        self.assertEqual(depth_one_no_stall["dequeue_cycle"], list(range(2, 14)))
        self.assertEqual(depth_one_no_stall["peak"], 1)
        self.assertEqual(depth_one_no_stall["source_stall_count"], 0)
        self.assertEqual(depth_one_no_stall["completion"], 13)
        depth_one_long = self.oracle(1, 8, False)["applied"]
        self.assertEqual(
            [index + 1 for index, event in enumerate(depth_one_long["source_paused"]) if event],
            list(range(5, 13)),
        )
        self.assertEqual(depth_one_long["completion"], 21)
        self.assertEqual(depth_one_long["lost_ids"], [])
        deep = self.oracle(6, 5, False)["applied"]
        self.assertEqual(deep["source_stall_count"], 0)
        self.assertEqual(deep["peak"], 6)
        self.assertEqual(deep["completion"], 18)
        maximum = self.oracle(6, 8, False)["applied"]
        self.assertEqual(maximum["source_stall_count"], 3)
        self.assertEqual(maximum["peak"], 6)
        self.assertEqual(maximum["completion"], 21)
        self.assertEqual(maximum["dequeued_ids"], list(range(1, 13)))

    def test_broken_ignore_ready_has_exact_loss_hold_and_sequence_symptom(self):
        healthy = self.oracle(3, 5, False)
        broken = self.oracle(3, 5, True)
        self.assertEqual(broken["reference"], healthy["applied"])
        path = broken["applied"]
        self.assertTrue(broken["fault_active"])
        self.assertEqual(
            [index + 1 for index, event in enumerate(path["drops"]) if event],
            [7, 8, 9],
        )
        self.assertEqual(
            [index + 1 for index, event in enumerate(path["source_hold_violations"]) if event],
            [8, 9, 10],
        )
        self.assertEqual(path["lost_ids"], [7, 8, 9])
        self.assertEqual(path["dequeued_ids"], [1, 2, 3, 4, 5, 6, 10, 11, 12])
        self.assertEqual(
            path["dequeued_codes"],
            [0, 411, 822, 1233, 1644, 2055, 3699, 14, 425],
        )
        self.assertEqual(path["drop_count"], 3)
        self.assertEqual(path["source_hold_violation_count"], 3)
        self.assertEqual(path["output_hold_violation_count"], 0)
        self.assertFalse(path["completed"])
        self.assertIsNone(path["completion"])
        self.assertLessEqual(max(path["occupancy_after"]), 3)
        self.assertEqual(path["final_conservation"], 0)
        self.assertEqual(path["final_queue"], [])
        inert_no_stall = self.oracle(3, 0, True)
        healthy_no_stall = self.oracle(3, 0, False)
        self.assertFalse(inert_no_stall["fault_active"])
        self.assertEqual(inert_no_stall["applied"], healthy_no_stall["applied"])
        inert_deep = self.oracle(6, 5, True)
        healthy_deep = self.oracle(6, 5, False)
        self.assertFalse(inert_deep["fault_active"])
        self.assertEqual(inert_deep["applied"], healthy_deep["applied"])

    def test_complete_control_grid_is_deterministic_isolated_and_resource_bounded(self):
        baseline = self.oracle()
        for depth in range(1, 7):
            for stall in range(9):
                healthy = self.oracle(depth, stall, False)
                healthy_again = self.oracle(depth, stall, False)
                broken = self.oracle(depth, stall, True)
                with self.subTest(depth=depth, stall=stall):
                    self.assertEqual(healthy, healthy_again)
                    path = healthy["applied"]
                    self.assertTrue(path["completed"])
                    self.assertLessEqual(path["completion"], 21)
                    self.assertEqual(path["enqueued_ids"], list(range(1, 13)))
                    self.assertEqual(path["dequeued_ids"], list(range(1, 13)))
                    self.assertEqual(path["dequeued_codes"], TOKEN_CODES)
                    self.assertEqual(path["lost_ids"], [])
                    self.assertFalse(any(path["source_hold_violations"]))
                    self.assertFalse(any(path["output_hold_violations"]))
                    self.assertTrue(all(value == 0 for value in path["recurrence"]))
                    self.assertEqual(path["final_conservation"], 0)
                    self.assertEqual(path["final_queue"], [])
                    self.assertLessEqual(max(path["occupancy_after"]), depth)
                    self.assertEqual(broken["reference"], path)
                    broken_path = broken["applied"]
                    self.assertEqual(
                        len(broken_path["dequeued_ids"])
                        + len(broken_path["lost_ids"]),
                        12,
                    )
                    self.assertEqual(
                        broken_path["drop_count"], len(broken_path["lost_ids"])
                    )
                    self.assertEqual(
                        broken_path["dequeued_ids"],
                        sorted(set(broken_path["dequeued_ids"])),
                    )
                    self.assertFalse(any(broken_path["output_hold_violations"]))
                    self.assertTrue(
                        all(value == 0 for value in broken_path["recurrence"])
                    )
                    self.assertEqual(broken_path["final_conservation"], 0)
                    self.assertEqual(broken_path["final_queue"], [])
                    self.assertEqual(path["record_values"], 24)
                    self.assertEqual(path["token_values"], 12)
                    self.assertEqual(healthy["maximum_depth"], 6)
                    self.assertEqual(healthy["payload_bits"], 12)
        maximum_call = self.oracle(6, 8, False)
        broken_call = self.oracle(3, 5, True)
        self.assertNotEqual(maximum_call, baseline)
        self.assertNotEqual(broken_call, baseline)
        self.assertEqual(self.oracle(), baseline)

    def test_malformed_inputs_reject_and_valid_call_recovers(self):
        baseline = self.oracle()
        malformed = [
            ((0, 5, False), "fifo_depth"),
            ((7, 5, False), "fifo_depth"),
            ((2.5, 5, False), "fifo_depth"),
            (([2, 3], 5, False), "fifo_depth"),
            ((True, 5, False), "fifo_depth"),
            ((3, -1, False), "consumer_stall_cycles"),
            ((3, 9, False), "consumer_stall_cycles"),
            ((3, 4.5, False), "consumer_stall_cycles"),
            ((3, [4, 5], False), "consumer_stall_cycles"),
            ((3, True, False), "consumer_stall_cycles"),
            ((3, 5, 2), "broken_ignore_backpressure"),
            ((3, 5, 0.5), "broken_ignore_backpressure"),
            ((3, 5, [False, True]), "broken_ignore_backpressure"),
        ]
        for args, marker in malformed:
            with self.subTest(args=args):
                with self.assertRaisesRegex(ValueError, marker):
                    self.oracle(*args)
                self.assertEqual(self.oracle(), baseline)
        for nonfinite in (math.nan, math.inf, -math.inf):
            with self.subTest(nonfinite=nonfinite, control="fifo_depth"):
                with self.assertRaisesRegex(ValueError, "fifo_depth"):
                    self.oracle(nonfinite, 5, False)
                self.assertEqual(self.oracle(), baseline)
            with self.subTest(nonfinite=nonfinite, control="consumer_stall"):
                with self.assertRaisesRegex(ValueError, "consumer_stall_cycles"):
                    self.oracle(3, nonfinite, False)
                self.assertEqual(self.oracle(), baseline)
            with self.subTest(nonfinite=nonfinite, control="fault"):
                with self.assertRaisesRegex(
                    ValueError, "broken_ignore_backpressure"
                ):
                    self.oracle(3, 5, nonfinite)
                self.assertEqual(self.oracle(), baseline)
        for complex_value in (3 + 1j, 5 + 1j, 1 + 1j):
            with self.subTest(complex_value=complex_value):
                if complex_value.real == 3:
                    args = (complex_value, 5, False)
                    marker = "fifo_depth"
                elif complex_value.real == 5:
                    args = (3, complex_value, False)
                    marker = "consumer_stall_cycles"
                else:
                    args = (3, 5, complex_value)
                    marker = "broken_ignore_backpressure"
                with self.assertRaisesRegex(ValueError, marker):
                    self.oracle(*args)
                self.assertEqual(self.oracle(), baseline)
        self.assertEqual(self.oracle(3, 5, 0), baseline)
        self.assertEqual(self.oracle(3, 5, 1), self.oracle(3, 5, True))


if __name__ == "__main__":
    unittest.main()
