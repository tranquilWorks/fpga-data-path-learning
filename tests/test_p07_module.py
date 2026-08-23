from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_FOLDER = ROOT / "modules/07-trade-resources-for-throughput"
GUIDING_QUESTION = (
    "What inputs, observable effects, and failure modes matter when you trade "
    "Resources for Throughput?"
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
EXPECTED_BASE_INPUTS = [3, -2, 5, 1, -4, 6, -1, 4]
EXPECTED_COEFFICIENTS = [2, 4, -1, 3, 2, -2, 5, 5]
EXPECTED_CHECKSUMS = [-9, 72, 23, -16, 69, -6]


class P07ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "curriculum/modules.json").read_text(encoding="utf-8")
        )
        cls.module = next(
            module for module in cls.manifest["modules"] if module["id"] == "P07"
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
                "number": 7,
                "id": "P07",
                "title": "Trade Resources for Throughput",
                "guiding_question": GUIDING_QUESTION,
                "phase": 2,
                "phase_title": "Numeric hardware",
                "slug": "trade-resources-for-throughput",
                "folder": "modules/07-trade-resources-for-throughput",
                "implementation_batch": "P07",
                "prerequisites": ["P06"],
                "status": "implemented",
                "evidence_level": "simulated",
            },
        )
        p06 = next(
            module for module in self.manifest["modules"] if module["id"] == "P06"
        )
        self.assertEqual(p06["status"], "implemented")
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
            "p06",
            "product code",
            "valid",
            "two-cycle",
            "lane initiation interval",
            "ceil",
            "finite",
        ):
            self.assertIn(marker, lesson)
        for marker in ("read", "baseline", "lever 1", "lever 2", "mechanism first"):
            self.assertIn(marker, lesson)
        self.assertIn("make no second prediction", lesson)
        self.assertIn("make no second prediction", walkthrough)
        self.assertIn("one prompt at a time", checks)
        self.assertIn("limiting-case check", checks)
        self.assertIn("teach-back", checks)
        self.assertIn("two sentences", checks)
        for limitation in (
            "dsp slice",
            "timing",
            "reduction",
            "backpressure",
            "fifo",
        ):
            self.assertIn(limitation, lesson)

    def test_model_is_transparent_deterministic_bounded_and_presentation_free(self):
        source = self.read("model.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        for expression in (
            "baseInputCodeSequence=[3-251-46-14].';",
            "coefficientCodeSequence=[24-132-255].';",
            "sourceIndexByFrame(:,frameNumber)=mod(operationIndex-frameNumber,operationCount)+1;",
            "productCodeByFrame=inputCodeByFrame.*coefficientCodeByFrame;",
            "capacityInitiationIntervalCycles=ceil(operationCount/resourceUnits);",
            "floorIssueCyclesPerFrame=floor(operationCount/resourceUnits);",
            "scheduledSlotCountPerFrame=resourceUnits*scheduledIssueCyclesPerFrame;",
            "actualProductValidByFrame=repmat(operationIndex<=scheduledOperationCountPerFrame,1,frameCount);",
            "actualResultCycle(validOperations,frameNumber)=actualIssueCycle(validOperations,frameNumber)+pipelineLatencyCycles;",
            "requiredResourceUnitsForOfferedInterval=ceil(operationCount/offeredFrameInterval);",
        ):
            self.assertIn(expression, compact)
        self.assertIn(
            "referenceStartCycle(frameNumber)=max(arrivalCycle(frameNumber),referenceStartCycle(frameNumber-1)+capacityInitiationIntervalCycles);",
            compact,
        )
        for field in (
            "productCodeByFrame",
            "actualProductValidByFrame",
            "referenceIssueCycle",
            "actualIssueCycle",
            "actualLaneIndex",
            "referenceCompletionCycle",
            "claimedCompletionCycle",
            "capacityInitiationIntervalCycles",
            "scheduledOutputIntervalCycles",
            "packingUtilization",
            "idleLaneSlotsPerFrame",
            "referenceWaitCycles",
            "droppedOperationCountPerFrame",
            "issueCollisionCount",
            "modeledProductPipelineStorageBits",
            "maxTimelineCycles",
        ):
            self.assertIn(field, source)
        for identifier in (
            "P07:InvalidResourceUnits",
            "P07:InvalidOfferedFrameInterval",
            "P07:InvalidSelectedFrame",
            "P07:InvalidBrokenFloorSchedule",
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
        for opaque_stateful_or_external in (
            "fi(",
            "numerictype",
            "fimath",
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
        ):
            self.assertNotIn(opaque_stateful_or_external, lower)
        self.assertIsNone(re.search(r"(?m)^\s*while\b", lower))

    def test_accepted_numeric_classes_have_behavioral_equivalence_check(self):
        compact_model = re.sub(r"\s+", "", self.read("model.m")).replace("...", "")
        for conversion in (
            "resourceUnits=double(resourceUnits);",
            "offeredFrameInterval=double(offeredFrameInterval);",
            "selectedFrame=double(selectedFrame);",
            "brokenFloorSchedule=logical(brokenFloorSchedule);",
        ):
            self.assertIn(conversion, compact_model)
        compact_checks = re.sub(r"\s+", "", self.read("run_checks.m")).replace(
            "...", ""
        )
        self.assertIn(
            "typedBaseline=model(uint8(2),int8(4),single(3),uint8(0));",
            compact_checks,
        )
        self.assertIn("isequaln(typedBaseline,baseline)", compact_checks)
        self.assertIn("P07:NumericClassNormalization", self.read("run_checks.m"))

    def test_experiment_has_independent_sweeps_labels_metrics_and_broken_case(self):
        source = self.read("experiment.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        self.assertGreaterEqual(source.count("%%"), 6)
        self.assertIn("sweep 1", lower)
        self.assertIn("sweep 2", lower)
        self.assertIn("resourceCounts=1:8;", compact)
        self.assertIn("offeredIntervals=1:8;", compact)
        self.assertIn("model(resourceCounts(sweepIndex),1,3,false)", compact)
        self.assertIn("model(2,offeredIntervals(sweepIndex),3,false)", compact)
        self.assertIn("resource sweep must preserve source arrivals", lower)
        self.assertIn("offered-interval sweep must preserve resources", lower)
        self.assertIn("deliberately broken case", lower)
        self.assertIn("healthy=model(3,2,3,false);", compact)
        self.assertIn("broken=model(3,2,3,true);", compact)
        self.assertIn("resourceunits*issuecycles must cover all eight", lower)
        self.assertIn("selecteddroppedoperationindices,[7;8]", compact.lower())
        self.assertGreaterEqual(lower.count("xlabel("), 15)
        self.assertGreaterEqual(lower.count("ylabel("), 15)
        for unit_marker in (
            "[cycles]",
            "[cycles/frame]",
            "[frames/cycle]",
            "[modeled multiplier index]",
            "[operation index]",
            "[signed product code]",
            "[binary valid]",
        ):
            self.assertIn(unit_marker, lower)
        for metric in (
            "packing",
            "idle",
            "max wait",
            "scheduled rate",
            "complete frames",
            "dropped operations",
        ):
            self.assertIn(metric, lower)
        self.assertNotIn("close all", lower)

    def test_interactive_controls_are_bounded_model_backed_and_fault_safe(self):
        source = self.read("interactive.m")
        lower = source.lower()
        self.assertIn("modelFcn = @model", source)
        self.assertGreaterEqual(lower.count("uispinner("), 3)
        self.assertIn("uicheckbox(", lower)
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*1\s+8\s*\]")
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*1\s+6\s*\]")
        self.assertGreaterEqual(source.count("ValueChangedFcn"), 4)
        self.assertIn("mod(8,resourceUnits) == 0", source)
        clear_fault = source.index("faultCheckbox.Value = false")
        disable_fault = source.index("faultCheckbox.Enable = 'off'")
        self.assertLess(clear_fault, disable_fault)
        for phrase in (
            "lanes set raw work",
            "complete-frame capacity",
            "source sets demand",
            "dropped",
            "assumed",
            "modeled bits",
        ):
            self.assertIn(phrase, lower)
        self.assertIn("raw lane work=%d products/cycle", source)
        self.assertIn("non-preemptive frame capacity=%g frames/cycle", source)
        self.assertIn("scheduled rate correct/claimed", source)
        self.assertIn("packing correct/claimed", source)
        self.assertNotIn("close all", lower)

    def test_checks_cover_limits_fault_validation_recovery_and_resource_bounds(self):
        source = self.read("run_checks.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "").lower()
        self.assertGreaterEqual(lower.count("assert("), 35)
        self.assertIn("expectedchecksums=[-97223-1669-6].';", compact)
        self.assertIn("expectedcapacityintervals=[84322221];", compact)
        self.assertIn("expectedscheduledintervals=[44445678];", compact)
        self.assertIn("expectedqueuedepths=[43200000];", compact)
        self.assertIn("expectedbrokenchecksums", compact)
        self.assertIn("forresourceunits=1:8", compact)
        self.assertIn("forofferedframeinterval=1:8", compact)
        for identifier in (
            "P07:BaselineProducts",
            "P07:BinaryPoint",
            "P07:BaselineSchedule",
            "P07:NumericClassNormalization",
            "P07:ResourceSweep",
            "P07:ResourceSweepIsolation",
            "P07:NonPreemptivePartialGroup",
            "P07:DemandSweep",
            "P07:DemandSweepIsolation",
            "P07:DemandQueueRecurrence",
            "P07:HealthyGrid",
            "P07:LaneExclusivity",
            "P07:ResourceBound",
            "P07:SerialLimit",
            "P07:FullReplicationLimit",
            "P07:BrokenTailLoss",
            "P07:BrokenThroughputClaim",
            "P07:BrokenIsolation",
            "P07:BrokenInertDivisor",
            "P07:BrokenNonDivisorGrid",
            "P07:SelectedViewIsolation",
            "P07:DeterminismRecovery",
            "P07:InvalidResourceUnits",
            "P07:InvalidOfferedFrameInterval",
            "P07:InvalidSelectedFrame",
            "P07:InvalidBrokenFloorSchedule",
        ):
            self.assertIn(identifier.lower(), lower)
        self.assertIn("p07 checks passed", lower)

    def test_p07_text_files_have_exactly_one_terminal_newline(self):
        for name in REQUIRED_ARTIFACTS:
            with self.subTest(artifact=name):
                data = (MODULE_FOLDER / name).read_bytes()
                self.assertTrue(data.endswith(b"\n"))
                self.assertFalse(data.endswith(b"\n\n"))
                self.assertNotIn(b"\r", data)


class P07IndependentOracleTests(unittest.TestCase):
    @staticmethod
    def oracle(
        resource_units: int = 2,
        offered_interval: int = 4,
        selected_frame: int = 3,
        broken_floor: bool = False,
    ):
        if type(resource_units) is not int or not 1 <= resource_units <= 8:
            raise ValueError("resource_units")
        if type(offered_interval) is not int or not 1 <= offered_interval <= 8:
            raise ValueError("offered_interval")
        if type(selected_frame) is not int or not 1 <= selected_frame <= 6:
            raise ValueError("selected_frame")
        valid_flag = type(broken_floor) is bool or (
            type(broken_floor) is int and broken_floor in (0, 1)
        )
        if not valid_flag:
            raise ValueError("broken_floor")
        broken_floor = bool(broken_floor)

        operation_count = 8
        frame_count = 6
        latency = 2
        product_frames = []
        for frame in range(frame_count):
            shifted = (
                EXPECTED_BASE_INPUTS[-frame:] + EXPECTED_BASE_INPUTS[:-frame]
                if frame
                else EXPECTED_BASE_INPUTS.copy()
            )
            product_frames.append(
                [value * coefficient for value, coefficient in zip(shifted, EXPECTED_COEFFICIENTS)]
            )

        capacity_groups = math.ceil(operation_count / resource_units)
        floor_groups = operation_count // resource_units
        scheduled_groups = floor_groups if broken_floor else capacity_groups
        arrivals = [1 + frame * offered_interval for frame in range(frame_count)]

        def starts_for(groups):
            starts = []
            for arrival in arrivals:
                starts.append(arrival if not starts else max(arrival, starts[-1] + groups))
            return starts

        reference_starts = starts_for(capacity_groups)
        scheduled_starts = starts_for(scheduled_groups)
        reference_issue = [
            [start + operation // resource_units for operation in range(operation_count)]
            for start in reference_starts
        ]
        reference_lane = [
            [1 + operation % resource_units for operation in range(operation_count)]
            for _ in range(frame_count)
        ]
        reference_result = [
            [issue + latency for issue in frame] for frame in reference_issue
        ]
        reference_completion = [max(frame) for frame in reference_result]

        covered = min(operation_count, resource_units * scheduled_groups)
        actual_valid = [
            [operation < covered for operation in range(operation_count)]
            for _ in range(frame_count)
        ]
        actual_issue = [
            [
                start + operation // resource_units if operation < covered else 0
                for operation in range(operation_count)
            ]
            for start in scheduled_starts
        ]
        actual_lane = [
            [
                1 + operation % resource_units if operation < covered else 0
                for operation in range(operation_count)
            ]
            for _ in range(frame_count)
        ]
        actual_result = [
            [issue + latency if issue else 0 for issue in frame]
            for frame in actual_issue
        ]
        claimed_completion = [
            start + scheduled_groups - 1 + latency for start in scheduled_starts
        ]
        actual_products = [
            [product if valid else 0 for product, valid in zip(products, validity)]
            for products, validity in zip(product_frames, actual_valid)
        ]
        checksums = [sum(products) for products in product_frames]
        actual_checksums = [sum(products) for products in actual_products]
        dropped = [
            [index + 1 for index, valid in enumerate(validity) if not valid]
            for validity in actual_valid
        ]

        issue_slots = {}
        result_slots = {}
        issue_collisions = 0
        result_collisions = 0
        for frame in range(frame_count):
            for operation in range(operation_count):
                if not actual_valid[frame][operation]:
                    continue
                issue_key = (actual_issue[frame][operation], actual_lane[frame][operation])
                result_key = (actual_result[frame][operation], actual_lane[frame][operation])
                issue_collisions += issue_key in issue_slots
                result_collisions += result_key in result_slots
                issue_slots[issue_key] = (frame + 1, operation + 1)
                result_slots[result_key] = (frame + 1, operation + 1)

        total_cycles = max(max(reference_completion), max(claimed_completion))
        reference_waits = [start - arrival for start, arrival in zip(reference_starts, arrivals)]
        scheduled_waits = [start - arrival for start, arrival in zip(scheduled_starts, arrivals)]
        reference_queue = [
            sum(arrival <= cycle < start for arrival, start in zip(arrivals, reference_starts))
            for cycle in range(1, total_cycles + 1)
        ]
        selected = selected_frame - 1
        return {
            "products": product_frames,
            "checksums": checksums,
            "actual_products": actual_products,
            "actual_checksums": actual_checksums,
            "capacity_groups": capacity_groups,
            "scheduled_groups": scheduled_groups,
            "arrivals": arrivals,
            "reference_starts": reference_starts,
            "scheduled_starts": scheduled_starts,
            "reference_issue": reference_issue,
            "reference_lane": reference_lane,
            "reference_result": reference_result,
            "reference_completion": reference_completion,
            "actual_valid": actual_valid,
            "actual_issue": actual_issue,
            "actual_lane": actual_lane,
            "actual_result": actual_result,
            "claimed_completion": claimed_completion,
            "covered": covered,
            "dropped": dropped,
            "complete_count": sum(all(validity) for validity in actual_valid),
            "reference_interval": max(offered_interval, capacity_groups),
            "scheduled_interval": max(offered_interval, scheduled_groups),
            "reference_rate": 1 / max(offered_interval, capacity_groups),
            "scheduled_rate": 1 / max(offered_interval, scheduled_groups),
            "utilization": operation_count / (resource_units * capacity_groups),
            "idle_slots": resource_units * capacity_groups - operation_count,
            "required_resources": math.ceil(operation_count / offered_interval),
            "reference_waits": reference_waits,
            "scheduled_waits": scheduled_waits,
            "reference_queue": reference_queue,
            "issue_collisions": issue_collisions,
            "result_collisions": result_collisions,
            "total_cycles": total_cycles,
            "timeline_slots": total_cycles * resource_units,
            "product_storage_bits": resource_units * latency * 8,
            "valid_storage_bits": resource_units * latency,
            "selected_products": product_frames[selected],
            "selected_actual_products": actual_products[selected],
            "selected_valid": actual_valid[selected],
            "selected_dropped": dropped[selected],
        }

    def test_exact_baseline_products_schedule_and_capacity(self):
        result = self.oracle()
        self.assertEqual(result["products"][0], [6, -8, -5, 3, -8, -12, -5, 20])
        self.assertEqual(result["checksums"], EXPECTED_CHECKSUMS)
        self.assertEqual(result["actual_checksums"], EXPECTED_CHECKSUMS)
        self.assertEqual((result["capacity_groups"], result["scheduled_groups"]), (4, 4))
        self.assertEqual(result["arrivals"], [1, 5, 9, 13, 17, 21])
        self.assertEqual(result["reference_starts"], result["arrivals"])
        self.assertEqual(result["reference_completion"], [6, 10, 14, 18, 22, 26])
        self.assertEqual(result["reference_issue"][0], [1, 1, 2, 2, 3, 3, 4, 4])
        self.assertEqual(result["reference_lane"][0], [1, 2, 1, 2, 1, 2, 1, 2])
        self.assertEqual(result["complete_count"], 6)
        self.assertEqual(result["reference_rate"], 0.25)
        self.assertEqual(max(result["reference_waits"]), 0)

    def test_resource_sweep_exposes_ceiling_plateaus_and_wait_tradeoff(self):
        results = [self.oracle(resource_units=value, offered_interval=1) for value in range(1, 9)]
        self.assertEqual([result["capacity_groups"] for result in results], [8, 4, 3, 2, 2, 2, 2, 1])
        self.assertEqual(
            [result["reference_completion"][0] - result["arrivals"][0] for result in results],
            [9, 5, 4, 3, 3, 3, 3, 2],
        )
        self.assertEqual([max(result["reference_waits"]) for result in results], [35, 15, 10, 5, 5, 5, 5, 0])
        self.assertEqual([result["idle_slots"] for result in results], [0, 0, 1, 0, 2, 4, 6, 0])
        for result in results:
            self.assertEqual(result["checksums"], EXPECTED_CHECKSUMS)
            self.assertEqual(result["complete_count"], 6)

    def test_nonpreemptive_partial_group_does_not_cross_pack_frames(self):
        result = self.oracle(resource_units=3, offered_interval=1, selected_frame=1)
        self.assertEqual(result["reference_starts"], [1, 4, 7, 10, 13, 16])
        self.assertEqual(result["reference_issue"][0], [1, 1, 1, 2, 2, 2, 3, 3])

        occupied_slots = {}
        for frame, (issues, lanes) in enumerate(
            zip(result["reference_issue"], result["reference_lane"]), start=1
        ):
            for operation, (issue, lane) in enumerate(zip(issues, lanes), start=1):
                self.assertNotIn((issue, lane), occupied_slots)
                occupied_slots[(issue, lane)] = (frame, operation)

        self.assertNotIn((3, 3), occupied_slots)
        self.assertEqual(occupied_slots[(4, 1)], (2, 1))
        raw_lane_frame_equivalent_rate = 3 / 8
        self.assertEqual(result["reference_rate"], 1 / 3)
        self.assertGreater(raw_lane_frame_equivalent_rate, result["reference_rate"])
        self.assertAlmostEqual(
            result["reference_rate"],
            result["utilization"] * raw_lane_frame_equivalent_rate,
        )

    def test_demand_sweep_is_capacity_limited_then_source_limited(self):
        results = [self.oracle(2, interval) for interval in range(1, 9)]
        self.assertEqual([result["reference_interval"] for result in results], [4, 4, 4, 4, 5, 6, 7, 8])
        self.assertEqual([max(result["reference_waits"]) for result in results], [15, 10, 5, 0, 0, 0, 0, 0])
        self.assertEqual([max(result["reference_queue"]) for result in results], [4, 3, 2, 0, 0, 0, 0, 0])
        self.assertEqual([result["required_resources"] for result in results], [8, 4, 3, 2, 2, 2, 2, 1])
        self.assertEqual([result["reference_rate"] for result in results], [0.25, 0.25, 0.25, 0.25, 0.2, 1 / 6, 1 / 7, 0.125])
        for result in results:
            self.assertEqual(result["capacity_groups"], 4)
            self.assertEqual(result["products"], results[0]["products"])
            queue_depth = 0
            expected_queue = []
            for cycle in range(1, result["total_cycles"] + 1):
                queue_depth += result["arrivals"].count(cycle)
                queue_depth -= result["reference_starts"].count(cycle)
                expected_queue.append(queue_depth)
            self.assertEqual(result["reference_queue"], expected_queue)

    def test_healthy_grid_covers_each_operation_once_and_is_resource_bounded(self):
        for resource_units in range(1, 9):
            for offered_interval in range(1, 9):
                result = self.oracle(resource_units, offered_interval, 6, False)
                with self.subTest(resource_units=resource_units, offered_interval=offered_interval):
                    self.assertEqual(result["complete_count"], 6)
                    self.assertTrue(all(all(validity) for validity in result["actual_valid"]))
                    self.assertEqual(result["actual_products"], result["products"])
                    self.assertEqual(result["actual_checksums"], EXPECTED_CHECKSUMS)
                    self.assertEqual(result["issue_collisions"], 0)
                    self.assertEqual(result["result_collisions"], 0)
                    self.assertLessEqual(result["total_cycles"], 50)
                    self.assertLessEqual(result["timeline_slots"], 400)
                    self.assertLessEqual(result["product_storage_bits"], 128)
                    self.assertLessEqual(result["valid_storage_bits"], 16)
                    for frame in range(6):
                        self.assertEqual(
                            result["actual_lane"][frame],
                            [1 + operation % resource_units for operation in range(8)],
                        )
                        self.assertEqual(
                            result["actual_result"][frame],
                            [issue + 2 for issue in result["actual_issue"][frame]],
                        )

    def test_serial_full_replication_and_supply_limited_cases(self):
        serial = self.oracle(1, 8, 1)
        self.assertEqual(serial["actual_issue"][0], list(range(1, 9)))
        self.assertEqual(serial["actual_lane"][0], [1] * 8)
        self.assertEqual(serial["reference_completion"][0], 10)
        fully_replicated = self.oracle(8, 1, 1)
        self.assertEqual(fully_replicated["actual_issue"][0], [1] * 8)
        self.assertEqual(fully_replicated["actual_lane"][0], list(range(1, 9)))
        self.assertEqual(fully_replicated["reference_completion"][0], 3)
        supply_limited = self.oracle(4, 8, 1)
        self.assertEqual((supply_limited["capacity_groups"], supply_limited["reference_interval"]), (2, 8))
        self.assertEqual(max(supply_limited["reference_waits"]), 0)

    def test_broken_floor_schedule_drops_exact_tail_and_overstates_rate(self):
        healthy = self.oracle(3, 2, 3, False)
        broken = self.oracle(3, 2, 3, True)
        self.assertEqual(broken["capacity_groups"], 3)
        self.assertEqual(broken["scheduled_groups"], 2)
        self.assertEqual(broken["reference_starts"], [1, 4, 7, 10, 13, 16])
        self.assertEqual(broken["scheduled_starts"], [1, 3, 5, 7, 9, 11])
        self.assertEqual(broken["reference_completion"], [5, 8, 11, 14, 17, 20])
        self.assertEqual(broken["claimed_completion"], [4, 6, 8, 10, 12, 14])
        self.assertEqual(broken["covered"], 6)
        self.assertEqual(broken["dropped"], [[7, 8]] * 6)
        self.assertEqual(broken["complete_count"], 0)
        self.assertEqual(broken["actual_checksums"], [-24, 47, 13, -1, 39, -21])
        self.assertEqual(broken["selected_valid"], [True] * 6 + [False] * 2)
        self.assertEqual(broken["scheduled_rate"], 0.5)
        self.assertEqual(healthy["reference_rate"], 1 / 3)
        self.assertEqual(broken["products"], healthy["products"])

    def test_fault_is_inert_for_divisors_and_bounded_for_nondivisors(self):
        for resource_units in range(1, 9):
            for offered_interval in range(1, 9):
                healthy = self.oracle(resource_units, offered_interval, 2, False)
                broken = self.oracle(resource_units, offered_interval, 2, True)
                with self.subTest(resource_units=resource_units, offered_interval=offered_interval):
                    self.assertEqual(broken["products"], healthy["products"])
                    self.assertEqual(broken["issue_collisions"], 0)
                    self.assertEqual(broken["result_collisions"], 0)
                    self.assertLessEqual(broken["total_cycles"], 50)
                    self.assertLessEqual(broken["timeline_slots"], 400)
                    if 8 % resource_units == 0:
                        self.assertEqual(broken["actual_products"], healthy["actual_products"])
                        self.assertEqual(broken["actual_issue"], healthy["actual_issue"])
                        self.assertEqual(broken["complete_count"], 6)
                    else:
                        covered = resource_units * (8 // resource_units)
                        self.assertEqual(broken["covered"], covered)
                        self.assertEqual(broken["selected_dropped"], list(range(covered + 1, 9)))
                        self.assertEqual(broken["complete_count"], 0)

    def test_malformed_inputs_reject_and_valid_call_recovers(self):
        invalid_calls = (
            (0, 4, 3, False),
            (9, 4, 3, False),
            (2.5, 4, 3, False),
            ([2, 3], 4, 3, False),
            (math.nan, 4, 3, False),
            (math.inf, 4, 3, False),
            (1 + 0j, 4, 3, False),
            (True, 4, 3, False),
            (2, 0, 3, False),
            (2, 9, 3, False),
            (2, 1.5, 3, False),
            (2, [4, 5], 3, False),
            (2, math.nan, 3, False),
            (2, math.inf, 3, False),
            (2, 1 + 0j, 3, False),
            (2, True, 3, False),
            (2, 4, 0, False),
            (2, 4, 7, False),
            (2, 4, 2.5, False),
            (2, 4, [2, 3], False),
            (2, 4, math.nan, False),
            (2, 4, math.inf, False),
            (2, 4, 1 + 0j, False),
            (2, 4, True, False),
            (2, 4, 3, 2),
            (2, 4, 3, 0.5),
            (2, 4, 3, [False, True]),
            (2, 4, 3, math.nan),
            (2, 4, 3, math.inf),
            (2, 4, 3, 1 + 0j),
        )
        expected = self.oracle()
        for arguments in invalid_calls:
            with self.subTest(arguments=arguments):
                with self.assertRaises(ValueError):
                    self.oracle(*arguments)
                self.assertEqual(self.oracle(), expected)

    def test_determinism_selected_view_isolation_and_recovery(self):
        first = self.oracle(3, 2, 1, False)
        last = self.oracle(3, 2, 6, False)
        for field in (
            "products",
            "checksums",
            "reference_starts",
            "reference_issue",
            "actual_issue",
            "actual_valid",
            "reference_waits",
            "reference_queue",
        ):
            self.assertEqual(first[field], last[field])
        self.oracle(7, 8, 6, True)
        self.assertEqual(self.oracle(3, 2, 1, False), first)


if __name__ == "__main__":
    unittest.main()
