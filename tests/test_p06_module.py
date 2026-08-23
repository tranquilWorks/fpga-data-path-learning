from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_FOLDER = ROOT / "modules/06-pipeline-a-multiply-accumulate"
GUIDING_QUESTION = (
    "What inputs, observable effects, and failure modes matter when you pipeline "
    "a Multiply-Accumulate?"
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
EXPECTED_INPUT_CODES = [3, -2, 5, 1, -4, 6, -1, 4]
EXPECTED_COEFFICIENT_CODES = [2, 4, -1, 3, 2, -2, 5, 5]
EXPECTED_PRODUCT_CODES = [6, -8, -5, 3, -8, -12, -5, 20]
EXPECTED_PREFIX_CODES = [6, -2, -7, -4, -12, -24, -29, -9]


class P06ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "curriculum/modules.json").read_text(encoding="utf-8")
        )
        cls.module = next(
            module for module in cls.manifest["modules"] if module["id"] == "P06"
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
                "number": 6,
                "id": "P06",
                "title": "Pipeline a Multiply-Accumulate",
                "guiding_question": GUIDING_QUESTION,
                "phase": 2,
                "phase_title": "Numeric hardware",
                "slug": "pipeline-a-multiply-accumulate",
                "folder": "modules/06-pipeline-a-multiply-accumulate",
                "implementation_batch": "P06",
                "prerequisites": ["P05"],
                "status": "implemented",
                "evidence_level": "simulated",
            },
        )
        p05 = next(
            module for module in self.manifest["modules"] if module["id"] == "P05"
        )
        self.assertEqual(p05["status"], "implemented")
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
            "p05",
            "binary-point",
            "w=4",
            "i=1",
            "excluding sign",
            "f=2",
            "product lsb",
            "post-edge",
            "no separately modeled adder-register delay",
        ):
            self.assertIn(marker, lesson)
        for marker in ("read", "baseline", "lever 1", "lever 2", "mechanism first"):
            self.assertIn(marker, lesson)
        self.assertIn("make no second prediction", lesson)
        self.assertIn("make no second prediction", walkthrough)
        self.assertIn("one prompt at a time", checks)
        self.assertIn("teach-back", checks)
        self.assertIn("two sentences", checks)
        for limitation in ("synthesis", "timing", "converter", "feedback"):
            self.assertIn(limitation, lesson)

    def test_model_is_transparent_deterministic_bounded_and_presentation_free(self):
        source = self.read("model.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        for expression in (
            "inputCodeSequence=[3-251-46-14].';",
            "coefficientCodeSequence=[24-132-255].';",
            "productCodeSequence=inputCodeSequence.*coefficientCodeSequence;",
            "operandWordLength=1+operandIntegerBits+operandFractionBits;",
            "productCodeWordLength=2*operandWordLength;",
            "productFractionBits=2*operandFractionBits;",
            "productLsb=2.^(-productFractionBits);",
            "lastInputCycle=1+(sampleCount-1)*inputPeriod;",
            "totalCycles=lastInputCycle+pipelineStages;",
            "inputValid=mod(cycle-1,inputPeriod)==0&cycle<=lastInputCycle;",
            "bubbleProductCode=bubbleInputCode*bubbleCoefficientCode;",
            "referenceAccumulatorProductCode(cycleIndex)=previousProduct(end);",
            "nextProduct(stageIndex)=previousProduct(stageIndex-1);",
            "accumulatorValid=inputValid;",
            "actualCode=actualCode+accumulatorProductCode(cycleIndex);",
            "referenceCode=referenceCode+referenceAccumulatorProductCode(cycleIndex);",
            "modeledAccumulatorWordLength=productCodeWordLength+ceil(log2(sampleCount));",
        ):
            self.assertIn(expression, compact)
        for field in (
            "inputTokenIndex",
            "productStageBefore",
            "productStageAfter",
            "referenceAccumulatorProductCode",
            "referenceAccumulatorValid",
            "referenceAccumulatorTokenIndex",
            "runningSumCode",
            "referenceRunningSumCode",
            "claimedTokenMismatchCount",
            "droppedTokenIndices",
            "referenceValidCycles",
            "minimumSequenceAccumulatorBits",
            "modeledAccumulatorWordLength",
            "modeledProductStorageBits",
        ):
            self.assertIn(field, source)
        for identifier in (
            "P06:InvalidPipelineStages",
            "P06:InvalidInputPeriod",
            "P06:InvalidSelectedCycle",
            "P06:InvalidBrokenValidAlignment",
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
            "pipelineStages=double(pipelineStages);",
            "inputPeriod=double(inputPeriod);",
            "selectedCycle=double(selectedCycle);",
            "brokenValidAlignment=logical(brokenValidAlignment);",
        ):
            self.assertIn(conversion, compact_model)
        compact_checks = re.sub(r"\s+", "", self.read("run_checks.m")).replace(
            "...", ""
        )
        self.assertIn(
            "typedBaseline=model(uint8(2),int8(1),single(5),uint8(0));",
            compact_checks,
        )
        self.assertIn("isequaln(typedBaseline,baseline)", compact_checks)
        self.assertIn("P06:NumericClassNormalization", self.read("run_checks.m"))

    def test_experiment_has_independent_sweeps_labels_metrics_and_broken_case(self):
        source = self.read("experiment.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        self.assertGreaterEqual(source.count("%%"), 6)
        self.assertIn("sweep 1", lower)
        self.assertIn("sweep 2", lower)
        self.assertIn("pipelineStageCounts=0:4;", compact)
        self.assertIn("inputPeriods=1:4;", compact)
        self.assertIn("model(pipelineStageCounts(sweepIndex),1,5,false)", compact)
        self.assertIn("model(2,inputPeriods(sweepIndex),5,false)", compact)
        self.assertIn(
            "pipeline-stage sweep must preserve products and input cadence", lower
        )
        self.assertIn(
            "input-period sweep must preserve pipeline depth and products", lower
        )
        self.assertIn("deliberately broken case", lower)
        self.assertIn("healthy=model(2,1,5,false);", compact)
        self.assertIn("broken=model(2,1,5,true);", compact)
        self.assertIn("valid and token identity must receive exactly", lower)
        self.assertIn("token claimed by broken valid", lower)
        self.assertIn("product token actually present", lower)
        self.assertNotIn(" or final result ", lower)
        self.assertGreaterEqual(lower.count("xlabel("), 12)
        self.assertGreaterEqual(lower.count("ylabel("), 12)
        for unit_marker in (
            "[cycles]",
            "[cycles/product]",
            "[unitless product]",
            "[binary, vertically offset]",
            "[token index]",
            "[stages]",
            "[values]",
        ):
            self.assertIn(unit_marker, lower)
        for metric in (
            "first accumulation",
            "completion",
            "storage",
            "final mac",
            "dropped tokens",
            "mispaired",
        ):
            self.assertIn(metric, lower)
        self.assertNotIn("close all", lower)

    def test_interactive_controls_are_bounded_model_backed_and_recover_safely(self):
        source = self.read("interactive.m")
        lower = source.lower()
        self.assertIn("modelFcn = @model", source)
        self.assertGreaterEqual(lower.count("uispinner("), 3)
        self.assertIn("uicheckbox(", lower)
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*0\s+4\s*\]")
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*1\s+4\s*\]")
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*1\s+10\s*\]")
        self.assertGreaterEqual(source.count("ValueChangedFcn"), 4)
        self.assertIn("faultCheckbox.Value = false", source)
        self.assertIn("faultCheckbox.Enable = 'off'", source)
        self.assertIn("pipelineStages == 0", source)
        clamp = source.index("if cycleSpinner.Value > sizing.totalCycles")
        narrow = source.index("cycleSpinner.Limits = [1 sizing.totalCycles]")
        self.assertLess(clamp, narrow)
        for phrase in (
            "stages delay product and valid together",
            "input period inserts bubbles",
            "broken: valid/token bypass",
            "dropped tokens",
            "trace minimum",
        ):
            self.assertIn(phrase, lower)
        self.assertNotIn("close all", lower)

    def test_checks_cover_limits_fault_validation_recovery_and_resource_bounds(self):
        source = self.read("run_checks.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "").lower()
        self.assertGreaterEqual(lower.count("assert("), 30)
        self.assertIn("expectedproductcodes=[6-8-53-8-12-520].';", compact)
        self.assertIn("expectedprefixcodes=[6-2-7-4-12-24-29-9].';", compact)
        self.assertIn("expectedfirstcycles=1:5;", compact)
        self.assertIn("expectedcompletioncycles=8:12;", compact)
        self.assertIn("expectedperiodcompletioncycles=[10172431];", compact)
        self.assertIn("expectedbubblecounts=[071421];", compact)
        self.assertIn("forpipelinestages=0:4", compact)
        self.assertIn("forinputperiod=1:4", compact)
        self.assertIn("expectedclaimedtokens=(1:8).';", compact)
        self.assertIn("expecteddatatokensatclaims=[00123456].';", compact)
        for identifier in (
            "P06:BaselineCodes",
            "P06:BinaryPoint",
            "P06:BubblePoison",
            "P06:PostEdgeConvention",
            "P06:PrePostStageState",
            "P06:NumericClassNormalization",
            "P06:StageSweep",
            "P06:StageSweepIsolation",
            "P06:PeriodSweep",
            "P06:PeriodSweepIsolation",
            "P06:TokenOrder",
            "P06:BubbleHold",
            "P06:HealthyGrid",
            "P06:ResourceBound",
            "P06:AccumulatorResourceBound",
            "P06:BrokenTokenAssociation",
            "P06:BrokenTailLoss",
            "P06:BrokenIsolation",
            "P06:BrokenDepthGrid",
            "P06:BrokenResourceGrid",
            "P06:BrokenBubblePoison",
            "P06:BrokenInertLimit",
            "P06:SelectedViewIsolation",
            "P06:DeterminismRecovery",
            "P06:InvalidPipelineStages",
            "P06:InvalidInputPeriod",
            "P06:InvalidSelectedCycle",
            "P06:InvalidBrokenValidAlignment",
        ):
            self.assertIn(identifier.lower(), lower)
        self.assertIn("p06 checks passed", lower)

    def test_p06_text_files_have_exactly_one_terminal_newline(self):
        for name in REQUIRED_ARTIFACTS:
            with self.subTest(artifact=name):
                data = (MODULE_FOLDER / name).read_bytes()
                self.assertTrue(data.endswith(b"\n"))
                self.assertFalse(data.endswith(b"\n\n"))
                self.assertNotIn(b"\r", data)


class P06IndependentOracleTests(unittest.TestCase):
    @staticmethod
    def oracle(
        pipeline_stages: int = 2,
        input_period: int = 1,
        selected_cycle: int = 5,
        broken_valid_alignment: bool = False,
    ):
        if type(pipeline_stages) is not int or not 0 <= pipeline_stages <= 4:
            raise ValueError("pipeline_stages")
        if type(input_period) is not int or not 1 <= input_period <= 4:
            raise ValueError("input_period")
        total_cycles = 1 + 7 * input_period + pipeline_stages
        if type(selected_cycle) is not int or not 1 <= selected_cycle <= total_cycles:
            raise ValueError("selected_cycle")
        valid_flag = type(broken_valid_alignment) is bool or (
            type(broken_valid_alignment) is int
            and broken_valid_alignment in (0, 1)
        )
        if not valid_flag:
            raise ValueError("broken_valid_alignment")
        broken_valid_alignment = bool(broken_valid_alignment)

        input_valid = [False] * total_cycles
        input_token = [0] * total_cycles
        input_product = [-56] * total_cycles
        for token, product in enumerate(EXPECTED_PRODUCT_CODES, start=1):
            cycle_index = (token - 1) * input_period
            input_valid[cycle_index] = True
            input_token[cycle_index] = token
            input_product[cycle_index] = product

        previous_product = [0] * pipeline_stages
        previous_valid = [False] * pipeline_stages
        previous_token = [0] * pipeline_stages
        stage_before = []
        stage_after = []
        reference_product = []
        reference_valid = []
        reference_token = []
        for cycle_index in range(total_cycles):
            stage_before.append(previous_product.copy())
            if pipeline_stages == 0:
                reference_product.append(input_product[cycle_index])
                reference_valid.append(input_valid[cycle_index])
                reference_token.append(input_token[cycle_index])
                stage_after.append([])
                continue
            reference_product.append(previous_product[-1])
            reference_valid.append(previous_valid[-1])
            reference_token.append(previous_token[-1])
            next_product = [input_product[cycle_index], *previous_product[:-1]]
            next_valid = [input_valid[cycle_index], *previous_valid[:-1]]
            next_token = [input_token[cycle_index], *previous_token[:-1]]
            stage_after.append(next_product.copy())
            previous_product = next_product
            previous_valid = next_valid
            previous_token = next_token

        if broken_valid_alignment:
            actual_valid = input_valid.copy()
            valid_token = input_token.copy()
        else:
            actual_valid = reference_valid.copy()
            valid_token = reference_token.copy()

        running = []
        reference_running = []
        actual_code = 0
        reference_code = 0
        seen = set()
        for valid, expected_valid, product, data_token in zip(
            actual_valid, reference_valid, reference_product, reference_token
        ):
            if valid:
                actual_code += product
                if data_token:
                    seen.add(data_token)
            if expected_valid:
                reference_code += product
            running.append(actual_code)
            reference_running.append(reference_code)

        claimed_mismatch = [
            valid and claim != data
            for valid, claim, data in zip(actual_valid, valid_token, reference_token)
        ]
        valid_data_mismatch = [
            valid != expected_valid
            or (valid and expected_valid and claim != data)
            for valid, expected_valid, claim, data in zip(
                actual_valid, reference_valid, valid_token, reference_token
            )
        ]
        return {
            "total_cycles": total_cycles,
            "input_valid": input_valid,
            "input_token": input_token,
            "input_product": input_product,
            "stage_before": stage_before,
            "stage_after": stage_after,
            "reference_product": reference_product,
            "reference_valid": reference_valid,
            "reference_token": reference_token,
            "actual_valid": actual_valid,
            "valid_token": valid_token,
            "running": running,
            "reference_running": reference_running,
            "final_code": running[-1],
            "reference_final_code": reference_running[-1],
            "final_value": running[-1] / 16,
            "reference_final_value": reference_running[-1] / 16,
            "accumulated_tokens": sorted(seen),
            "dropped_tokens": [token for token in range(1, 9) if token not in seen],
            "empty_count": sum(
                valid and data == 0
                for valid, data in zip(actual_valid, reference_token)
            ),
            "mispaired_count": sum(
                valid and data > 0 and claim != data
                for valid, claim, data in zip(actual_valid, valid_token, reference_token)
            ),
            "claimed_mismatch_count": sum(claimed_mismatch),
            "valid_data_mismatch_cycles": [
                index + 1 for index, differs in enumerate(valid_data_mismatch) if differs
            ],
            "sum_mismatch_cycles": [
                index + 1
                for index, (actual, expected) in enumerate(
                    zip(running, reference_running)
                )
                if actual != expected
            ],
            "selected_running": running[selected_cycle - 1],
        }

    def test_exact_baseline_codes_binary_point_schedule_and_prefix_sum(self):
        result = self.oracle()
        self.assertEqual(
            [x * h for x, h in zip(EXPECTED_INPUT_CODES, EXPECTED_COEFFICIENT_CODES)],
            EXPECTED_PRODUCT_CODES,
        )
        self.assertEqual(result["input_valid"], [True] * 8 + [False] * 2)
        self.assertEqual(result["reference_valid"], [False] * 2 + [True] * 8)
        self.assertEqual(result["reference_product"], [0, 0, *EXPECTED_PRODUCT_CODES])
        self.assertEqual(result["reference_running"], [0, 0, *EXPECTED_PREFIX_CODES])
        self.assertEqual(result["running"], result["reference_running"])
        self.assertEqual((result["final_code"], result["final_value"]), (-9, -0.5625))
        self.assertEqual(result["stage_before"][:3], [[0, 0], [6, 0], [-8, 6]])
        self.assertEqual(result["stage_after"][:3], [[6, 0], [-8, 6], [-5, -8]])
        self.assertEqual(result["selected_running"], -7)

    def test_pipeline_stage_sweep_shifts_timeline_without_changing_arithmetic(self):
        results = [self.oracle(pipeline_stages=stages) for stages in range(5)]
        self.assertEqual([result["total_cycles"] for result in results], list(range(8, 13)))
        for stages, result in enumerate(results):
            with self.subTest(stages=stages):
                valid_cycles = [
                    index + 1
                    for index, valid in enumerate(result["reference_valid"])
                    if valid
                ]
                self.assertEqual(valid_cycles, list(range(1 + stages, 9 + stages)))
                self.assertEqual(result["reference_running"], [0] * stages + EXPECTED_PREFIX_CODES)
                self.assertEqual(result["final_code"], -9)
                self.assertEqual(result["accumulated_tokens"], list(range(1, 9)))
                self.assertTrue(
                    all(len(row) == stages for row in result["stage_after"])
                )

    def test_input_period_sweep_propagates_nonzero_bubbles_only_when_valid(self):
        results = [self.oracle(input_period=period) for period in range(1, 5)]
        self.assertEqual([result["total_cycles"] for result in results], [10, 17, 24, 31])
        for period, result in enumerate(results, start=1):
            with self.subTest(period=period):
                input_cycles = [1 + index * period for index in range(8)]
                output_cycles = [cycle + 2 for cycle in input_cycles]
                self.assertEqual(
                    [index + 1 for index, valid in enumerate(result["input_valid"]) if valid],
                    input_cycles,
                )
                self.assertEqual(
                    [index + 1 for index, valid in enumerate(result["reference_valid"]) if valid],
                    output_cycles,
                )
                self.assertTrue(
                    all(
                        value == -56
                        for value, valid in zip(result["input_product"], result["input_valid"])
                        if not valid
                    )
                )
                self.assertEqual(
                    [result["reference_running"][cycle - 1] for cycle in output_cycles],
                    EXPECTED_PREFIX_CODES,
                )
                for index in range(1, result["total_cycles"]):
                    if not result["reference_valid"][index]:
                        self.assertEqual(
                            result["reference_running"][index],
                            result["reference_running"][index - 1],
                        )
                self.assertEqual(result["final_code"], -9)

    def test_healthy_grid_obeys_token_order_and_fixed_resource_bounds(self):
        for stages in range(5):
            for period in range(1, 5):
                result = self.oracle(stages, period)
                with self.subTest(stages=stages, period=period):
                    self.assertLessEqual(result["total_cycles"], 33)
                    self.assertLessEqual(
                        sum(len(row) for row in result["stage_after"]), 132
                    )
                    self.assertEqual(result["running"], result["reference_running"])
                    self.assertEqual(result["reference_final_code"], -9)
                    self.assertEqual(result["accumulated_tokens"], list(range(1, 9)))
                    self.assertEqual(result["dropped_tokens"], [])
                    self.assertEqual(result["claimed_mismatch_count"], 0)
                    self.assertEqual(result["valid_data_mismatch_cycles"], [])

    def test_broken_valid_bypass_exposes_token_loss_and_zero_stage_limit(self):
        healthy = self.oracle(2, 1, 5, False)
        broken = self.oracle(2, 1, 5, True)
        self.assertEqual(broken["running"], [0, 0, 6, -2, -7, -4, -12, -24, -24, -24])
        self.assertEqual(broken["valid_token"][:8], list(range(1, 9)))
        self.assertEqual(broken["reference_token"][:8], [0, 0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(broken["empty_count"], 2)
        self.assertEqual(broken["mispaired_count"], 6)
        self.assertEqual(broken["claimed_mismatch_count"], 8)
        self.assertEqual(broken["accumulated_tokens"], list(range(1, 7)))
        self.assertEqual(broken["dropped_tokens"], [7, 8])
        self.assertEqual(broken["valid_data_mismatch_cycles"], list(range(1, 11)))
        self.assertEqual(broken["sum_mismatch_cycles"], [9, 10])
        self.assertEqual((broken["final_code"], broken["final_value"]), (-24, -1.5))
        self.assertEqual(broken["reference_running"], healthy["running"])
        for stages in range(1, 5):
            current = self.oracle(stages, 1, 5, True)
            consumed = 8 - stages
            self.assertEqual(current["empty_count"], stages)
            self.assertEqual(current["mispaired_count"], consumed)
            self.assertEqual(current["dropped_tokens"], list(range(consumed + 1, 9)))
            self.assertEqual(current["final_code"], sum(EXPECTED_PRODUCT_CODES[:consumed]))
        direct_healthy = self.oracle(0, 1, 5, False)
        direct_broken = self.oracle(0, 1, 5, True)
        self.assertEqual(direct_broken["running"], direct_healthy["running"])
        self.assertEqual(direct_broken["valid_data_mismatch_cycles"], [])
        self.assertEqual(direct_broken["dropped_tokens"], [])

    def test_all_broken_schedules_are_bounded_and_sparse_poison_is_visible(self):
        for stages in range(1, 5):
            for period in range(1, 5):
                result = self.oracle(stages, period, 5, True)
                with self.subTest(stages=stages, period=period):
                    self.assertEqual(sum(result["actual_valid"]), 8)
                    self.assertEqual(result["claimed_mismatch_count"], 8)
                    self.assertGreaterEqual(len(result["dropped_tokens"]), 1)
                    self.assertTrue(
                        all(-1024 <= code <= 1023 for code in result["running"])
                    )
        sparse = self.oracle(1, 4, 5, True)
        self.assertEqual(sparse["final_code"], -392)
        self.assertEqual(sparse["accumulated_tokens"], [])
        self.assertEqual(sparse["dropped_tokens"], list(range(1, 9)))
        self.assertEqual(sparse["empty_count"], 8)

    def test_malformed_inputs_reject_and_valid_call_recovers(self):
        invalid_calls = (
            (-1, 1, 5, False),
            (5, 1, 5, False),
            (2.5, 1, 5, False),
            ([2, 3], 1, 5, False),
            (math.nan, 1, 5, False),
            (math.inf, 1, 5, False),
            (1 + 0j, 1, 5, False),
            (True, 1, 5, False),
            (2, 0, 5, False),
            (2, 5, 5, False),
            (2, 1.5, 5, False),
            (2, [1, 2], 5, False),
            (2, math.nan, 5, False),
            (2, math.inf, 5, False),
            (2, 1 + 0j, 5, False),
            (2, True, 5, False),
            (0, 1, 0, False),
            (0, 1, 9, False),
            (4, 4, 34, False),
            (2, 1, 2.5, False),
            (2, 1, [2, 3], False),
            (2, 1, math.nan, False),
            (2, 1, math.inf, False),
            (2, 1, 1 + 0j, False),
            (2, 1, True, False),
            (2, 1, 5, 2),
            (2, 1, 5, 0.5),
            (2, 1, 5, [False, True]),
            (2, 1, 5, math.nan),
            (2, 1, 5, math.inf),
            (2, 1, 5, 1 + 0j),
        )
        expected = self.oracle()
        for arguments in invalid_calls:
            with self.subTest(arguments=arguments):
                with self.assertRaises(ValueError):
                    self.oracle(*arguments)
                self.assertEqual(self.oracle(), expected)

    def test_determinism_selected_view_isolation_and_maximum_timeline(self):
        first = self.oracle(2, 3, 1, False)
        last = self.oracle(2, 3, 24, False)
        for field in (
            "input_valid",
            "input_product",
            "stage_after",
            "reference_product",
            "reference_valid",
            "reference_token",
            "running",
            "reference_running",
        ):
            self.assertEqual(first[field], last[field])
        maximum = self.oracle(4, 4, 33, False)
        self.assertEqual(maximum["total_cycles"], 33)
        self.assertEqual(maximum["reference_final_code"], -9)
        self.oracle(4, 4, 33, True)
        self.assertEqual(self.oracle(2, 3, 1, False), first)


if __name__ == "__main__":
    unittest.main()
