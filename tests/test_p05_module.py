from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_FOLDER = ROOT / "modules/05-quantize-arithmetic-into-fixed-point"
GUIDING_QUESTION = (
    "What inputs, observable effects, and failure modes matter when you quantize "
    "Arithmetic into Fixed Point?"
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
EXPECTED_INPUT = [
    -2.9,
    -2.1,
    -1.9375,
    -1.81,
    -1.49,
    -1.26,
    -1.00,
    -0.76,
    -0.51,
    -0.31,
    -0.1875,
    -0.0625,
    0,
    0.0625,
    0.1875,
    0.31,
    0.51,
    0.76,
    1.00,
    1.26,
    1.49,
    1.81,
    1.9375,
    2.1,
    2.9,
]


class P05ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "curriculum/modules.json").read_text(encoding="utf-8")
        )
        cls.module = next(
            module for module in cls.manifest["modules"] if module["id"] == "P05"
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
                "number": 5,
                "id": "P05",
                "title": "Quantize Arithmetic into Fixed Point",
                "guiding_question": GUIDING_QUESTION,
                "phase": 2,
                "phase_title": "Numeric hardware",
                "slug": "quantize-arithmetic-into-fixed-point",
                "folder": "modules/05-quantize-arithmetic-into-fixed-point",
                "implementation_batch": "P05",
                "prerequisites": ["P04"],
                "status": "implemented",
                "evidence_level": "simulated",
            },
        )
        p04 = next(
            module for module in self.manifest["modules"] if module["id"] == "P04"
        )
        self.assertEqual(p04["status"], "implemented")
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
            "p04",
            "fsm",
            "symbolic",
            "weighted numeric codes",
            "two's-complement",
            "binary-point",
        ):
            self.assertIn(marker, lesson)
        for marker in ("read", "baseline", "lever 1", "lever 2", "mechanism first"):
            self.assertIn(marker, lesson)
        self.assertIn("make no second prediction", lesson)
        self.assertIn("make no second prediction", walkthrough)
        self.assertIn("one prompt at a time", checks)
        self.assertIn("teach-back", checks)
        self.assertIn("two sentences", checks)
        for limitation in ("synthesis", "converter", "spectral"):
            self.assertIn(limitation, lesson)

    def test_model_is_transparent_deterministic_bounded_and_presentation_free(self):
        source = self.read("model.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        for expression in (
            "sampleIndex=(1:25).';",
            "wordLength=signBits+integerBits+fractionBits;",
            "lsb=2.^(-fractionBits);",
            "minCode=-2.^(wordLength-1);",
            "maxCode=2.^(wordLength-1)-1;",
            "modeledCodeCount=2.^wordLength;",
            "rangeMinimum=minCode*lsb;",
            "rangeMaximum=maxCode*lsb;",
            "scaledInput=inputSignal/lsb;",
            "roundedCode=sign(scaledInput).*floor(abs(scaledInput)+0.5);",
            "referenceCode=min(max(roundedCode,minCode),maxCode);",
            "wrappedCode=mod(roundedCode-minCode,modeledCodeCount)+minCode;",
            "quantizedSignal=quantizedCode*lsb;",
            "overflowMask=roundedCode<minCode|roundedCode>maxCode;",
            "directionReversalMask=mismatchMask&quantizedSignal.*inputSignal<0;",
            "rmsInRangeError=sqrt(mean(inRangeErrors.^2));",
        ):
            self.assertIn(expression, compact)
        self.assertIn(
            "inputSignal=[-2.9-2.1-1.9375-1.81-1.49-1.26-1.00",
            compact,
        )
        for field in (
            "roundedCode",
            "referenceCode",
            "wrappedCode",
            "quantizedCode",
            "quantizedSignal",
            "referenceError",
            "quantizationError",
            "overflowMask",
            "mismatchSamples",
            "directionReversalCount",
            "rmsInRangeError",
            "maxInRangeAbsError",
            "wordLength",
            "modeledCodeCount",
        ):
            self.assertIn(field, source)
        for identifier in (
            "P05:InvalidFractionBits",
            "P05:InvalidIntegerBits",
            "P05:InvalidSelectedSample",
            "P05:InvalidBrokenWrap",
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
            "quantizer",
            "fixed.",
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

    def test_accepted_numeric_classes_have_behavioral_equivalence_check(self):
        model_source = re.sub(r"\s+", "", self.read("model.m")).replace("...", "")
        for conversion in (
            "fractionBits=double(fractionBits);",
            "integerBits=double(integerBits);",
            "selectedSample=double(selectedSample);",
        ):
            self.assertIn(conversion, model_source)

        checks = self.read("run_checks.m")
        compact_checks = re.sub(r"\s+", "", checks).replace("...", "")
        self.assertIn(
            "typedBaseline=model(uint8(3),int8(2),single(16),uint8(0));",
            compact_checks,
        )
        self.assertIn("isequaln(typedBaseline,baseline)", compact_checks)
        self.assertIn("P05:NumericClassNormalization", checks)

    def test_experiment_has_independent_sweeps_labels_metrics_and_broken_case(self):
        source = self.read("experiment.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        self.assertGreaterEqual(source.count("%%"), 6)
        self.assertIn("sweep 1", lower)
        self.assertIn("sweep 2", lower)
        self.assertIn("fractionalBitCounts=0:8;", compact)
        self.assertIn("integerBitCounts=0:4;", compact)
        self.assertIn(
            "model(fractionalBitCounts(sweepIndex),2,13,false)", compact
        )
        self.assertIn(
            "model(3,integerBitCounts(sweepIndex),13,false)", compact
        )
        self.assertIn(
            "fractional-bit sweep must preserve range allocation and inputs",
            lower,
        )
        self.assertIn(
            "integer-bit sweep must preserve fractional precision and inputs",
            lower,
        )
        self.assertIn("deliberately broken case", lower)
        self.assertIn("healthy=model(3,1,25,false);", compact)
        self.assertIn("broken=model(3,1,25,true);", compact)
        self.assertIn("overflow must saturate at the nearest endpoint", lower)
        self.assertIn("direction reversal", lower)
        self.assertNotIn("stairs(", lower)
        self.assertGreaterEqual(lower.count("'linestyle','none'"), 3)
        self.assertGreaterEqual(lower.count("xlabel("), 8)
        self.assertGreaterEqual(lower.count("ylabel("), 8)
        for unit_marker in (
            "[unitless]",
            "[samples]",
            "[bits]",
            "[bits, sign excluded]",
        ):
            self.assertIn(unit_marker, lower)
        for metric in (
            "lsb",
            "rms error",
            "word length",
            "overflowed sample count",
            "mismatches",
        ):
            self.assertIn(metric, lower)
        self.assertNotIn("close all", lower)

    def test_interactive_controls_are_bounded_model_backed_and_fault_safe(self):
        source = self.read("interactive.m")
        lower = source.lower()
        self.assertIn("modelFcn = @model", source)
        self.assertGreaterEqual(lower.count("uispinner("), 3)
        self.assertIn("uicheckbox(", lower)
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*0\s+8\s*\]")
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*0\s+4\s*\]")
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*1\s+25\s*\]")
        self.assertGreaterEqual(source.count("ValueChangedFcn"), 4)
        self.assertIn("faultCheckbox.Enable = 'off'", source)
        self.assertIn("faultCheckbox.Value = false", source)
        self.assertIn("healthy.overflowCount == 0", source)
        self.assertNotIn("stairs(", lower)
        self.assertGreaterEqual(lower.count("'linestyle','none'"), 2)
        for phrase in (
            "fraction bits set lsb spacing",
            "integer bits (sign excluded) set range",
            "declared saturation",
            "broken wrap",
            "direction reversals",
        ):
            self.assertIn(phrase, lower)
        self.assertNotIn("close all", lower)

    def test_checks_cover_limits_fault_validation_recovery_and_resource_bounds(self):
        source = self.read("run_checks.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "").lower()
        self.assertGreaterEqual(lower.count("assert("), 25)
        self.assertIn(
            "expectedroundedcode=[-23-17-16-14-12-10-8-6-4-2-2-10122468101214161723].';",
            compact,
        )
        self.assertIn("expectedlsbs=2.^(-fractionalbitcounts);", compact)
        self.assertIn("expectedwordlengths=3:11;", compact)
        self.assertIn("expectedoverflowcounts=[135000];", compact)
        self.assertIn("forfractionbits=0:8", compact)
        self.assertIn("forintegerbits=0:4", compact)
        self.assertIn("expectedmismatchsamples=[12232425].';", compact)
        for identifier in (
            "P05:BaselineVector",
            "P05:BaselineCodes",
            "P05:TiePolicy",
            "P05:EndpointAsymmetry",
            "P05:NumericClassNormalization",
            "P05:HalfLsbBound",
            "P05:PrecisionSweep",
            "P05:PrecisionIsolation",
            "P05:RangeSweep",
            "P05:RangeIsolation",
            "P05:FormatGrid",
            "P05:HealthyReference",
            "P05:BrokenWrap",
            "P05:BrokenSymptom",
            "P05:BrokenIsolation",
            "P05:BrokenInertLimit",
            "P05:ResourceBound",
            "P05:SelectedViewIsolation",
            "P05:DeterminismRecovery",
            "P05:InvalidFractionBits",
            "P05:InvalidIntegerBits",
            "P05:InvalidSelectedSample",
            "P05:InvalidBrokenWrap",
        ):
            self.assertIn(identifier.lower(), lower)
        self.assertIn("p05 checks passed", lower)

    def test_p05_text_files_have_exactly_one_terminal_newline(self):
        for name in REQUIRED_ARTIFACTS:
            with self.subTest(artifact=name):
                data = (MODULE_FOLDER / name).read_bytes()
                self.assertTrue(data.endswith(b"\n"))
                self.assertFalse(data.endswith(b"\n\n"))
                self.assertNotIn(b"\r", data)


class P05IndependentOracleTests(unittest.TestCase):
    @staticmethod
    def round_ties_away(value: float) -> int:
        if value == 0:
            return 0
        magnitude = math.floor(abs(value) + 0.5)
        return magnitude if value > 0 else -magnitude

    @classmethod
    def oracle(
        cls,
        fraction_bits: int = 3,
        integer_bits: int = 2,
        selected_sample: int = 16,
        broken_wrap: bool = False,
    ):
        if type(fraction_bits) is not int or not 0 <= fraction_bits <= 8:
            raise ValueError("fraction_bits")
        if type(integer_bits) is not int or not 0 <= integer_bits <= 4:
            raise ValueError("integer_bits")
        if type(selected_sample) is not int or not 1 <= selected_sample <= 25:
            raise ValueError("selected_sample")
        valid_flag = type(broken_wrap) is bool or (
            type(broken_wrap) is int and broken_wrap in (0, 1)
        )
        if not valid_flag:
            raise ValueError("broken_wrap")
        broken_wrap = bool(broken_wrap)

        word_length = 1 + integer_bits + fraction_bits
        lsb = 2.0**-fraction_bits
        min_code = -(2 ** (word_length - 1))
        max_code = 2 ** (word_length - 1) - 1
        code_count = 2**word_length
        rounded = [cls.round_ties_away(value / lsb) for value in EXPECTED_INPUT]
        saturated = [min(max(code, min_code), max_code) for code in rounded]
        wrapped = [((code - min_code) % code_count) + min_code for code in rounded]
        actual_codes = wrapped if broken_wrap else saturated
        actual = [code * lsb for code in actual_codes]
        reference = [code * lsb for code in saturated]
        overflow = [
            code < min_code or code > max_code
            for code in rounded
        ]
        mismatch = [
            actual_code != reference_code
            for actual_code, reference_code in zip(actual_codes, saturated)
        ]
        errors = [
            quantized - original
            for quantized, original in zip(actual, EXPECTED_INPUT)
        ]
        reference_errors = [
            quantized - original
            for quantized, original in zip(reference, EXPECTED_INPUT)
        ]
        in_range_errors = [
            error
            for error, is_overflow in zip(reference_errors, overflow)
            if not is_overflow
        ]
        selected = selected_sample - 1
        return {
            "word_length": word_length,
            "lsb": lsb,
            "half_lsb": lsb / 2,
            "min_code": min_code,
            "max_code": max_code,
            "code_count": code_count,
            "range_min": min_code * lsb,
            "range_max": max_code * lsb,
            "rounded": rounded,
            "saturated_codes": saturated,
            "wrapped_codes": wrapped,
            "codes": actual_codes,
            "actual": actual,
            "reference": reference,
            "overflow": overflow,
            "overflow_indices": [
                index + 1 for index, value in enumerate(overflow) if value
            ],
            "mismatch": mismatch,
            "mismatch_indices": [
                index + 1 for index, value in enumerate(mismatch) if value
            ],
            "direction_reversals": sum(
                quantized * original < 0
                for quantized, original, differs in zip(
                    actual, EXPECTED_INPUT, mismatch
                )
                if differs
            ),
            "errors": errors,
            "reference_errors": reference_errors,
            "max_in_range_error": max(abs(error) for error in in_range_errors),
            "rms_in_range_error": math.sqrt(
                sum(error**2 for error in in_range_errors) / len(in_range_errors)
            ),
            "overall_rms_error": math.sqrt(
                sum(error**2 for error in errors) / len(errors)
            ),
            "selected_input": EXPECTED_INPUT[selected],
            "selected_code": actual_codes[selected],
            "selected_output": actual[selected],
        }

    def test_exact_overflow_free_baseline_and_tie_policy(self):
        result = self.oracle()
        self.assertEqual(
            result["rounded"],
            [
                -23,
                -17,
                -16,
                -14,
                -12,
                -10,
                -8,
                -6,
                -4,
                -2,
                -2,
                -1,
                0,
                1,
                2,
                2,
                4,
                6,
                8,
                10,
                12,
                14,
                16,
                17,
                23,
            ],
        )
        self.assertEqual(result["rounded"], result["codes"])
        self.assertEqual(result["overflow_indices"], [])
        self.assertEqual((result["word_length"], result["lsb"]), (6, 0.125))
        self.assertEqual((result["range_min"], result["range_max"]), (-4, 3.875))
        self.assertEqual(result["rounded"][11:14], [-1, 0, 1])
        self.assertEqual(result["max_in_range_error"], result["half_lsb"])
        self.assertEqual(
            (result["selected_input"], result["selected_code"], result["selected_output"]),
            (0.31, 2, 0.25),
        )

    def test_fractional_bit_sweep_halves_lsb_and_isolates_precision(self):
        results = [self.oracle(fraction_bits=value) for value in range(9)]
        self.assertEqual([result["lsb"] for result in results], [2.0**-f for f in range(9)])
        self.assertEqual([result["word_length"] for result in results], list(range(3, 12)))
        expected_max_errors = [
            0.49,
            0.24,
            0.10,
            0.0625,
            0.025,
            0.010,
            0.00625,
            0.0025,
            0.00171875,
        ]
        for observed, expected in zip(
            [result["max_in_range_error"] for result in results],
            expected_max_errors,
        ):
            self.assertAlmostEqual(observed, expected, places=14)
        self.assertTrue(
            all(
                later["rms_in_range_error"] < earlier["rms_in_range_error"]
                for earlier, later in zip(results, results[1:])
            )
        )
        for result in results:
            self.assertEqual(result["overflow_indices"], [])
            self.assertEqual(result["range_min"], -4)
            self.assertLessEqual(
                result["max_in_range_error"],
                result["half_lsb"] + math.ulp(result["half_lsb"]),
            )

    def test_integer_bit_sweep_expands_range_at_fixed_precision(self):
        results = [self.oracle(integer_bits=value) for value in range(5)]
        self.assertEqual([result["lsb"] for result in results], [0.125] * 5)
        self.assertEqual(
            [result["range_min"] for result in results],
            [-1, -2, -4, -8, -16],
        )
        self.assertEqual(
            [result["range_max"] for result in results],
            [0.875, 1.875, 3.875, 7.875, 15.875],
        )
        self.assertEqual(
            [len(result["overflow_indices"]) for result in results],
            [13, 5, 0, 0, 0],
        )
        self.assertEqual(results[2]["actual"], results[3]["actual"])
        self.assertEqual(results[2]["actual"], results[4]["actual"])

    def test_all_formats_obey_code_error_and_resource_bounds(self):
        for fraction_bits in range(9):
            for integer_bits in range(5):
                with self.subTest(
                    fraction_bits=fraction_bits,
                    integer_bits=integer_bits,
                ):
                    healthy = self.oracle(fraction_bits, integer_bits, 25, False)
                    wrapped = self.oracle(fraction_bits, integer_bits, 1, True)
                    self.assertEqual(
                        healthy["word_length"],
                        1 + integer_bits + fraction_bits,
                    )
                    self.assertLessEqual(healthy["word_length"], 13)
                    self.assertLessEqual(healthy["code_count"], 8192)
                    self.assertEqual(len(healthy["actual"]), 25)
                    self.assertTrue(
                        all(
                            healthy["min_code"] <= code <= healthy["max_code"]
                            for code in healthy["codes"]
                        )
                    )
                    self.assertTrue(
                        all(
                            abs(error)
                            <= healthy["half_lsb"] + math.ulp(healthy["half_lsb"])
                            for error, overflow in zip(
                                healthy["reference_errors"],
                                healthy["overflow"],
                            )
                            if not overflow
                        )
                    )
                    self.assertTrue(
                        all(
                            not differs or overflow
                            for differs, overflow in zip(
                                wrapped["mismatch"],
                                wrapped["overflow"],
                            )
                        )
                    )
                    self.assertTrue(
                        all(
                            wrapped["min_code"] <= code <= wrapped["max_code"]
                            for code in wrapped["codes"]
                        )
                    )

    def test_broken_wrap_symptom_isolated_and_inert_without_overflow(self):
        healthy = self.oracle(3, 1, 25, False)
        broken = self.oracle(3, 1, 25, True)
        self.assertEqual(healthy["overflow_indices"], [1, 2, 23, 24, 25])
        self.assertEqual(
            [healthy["actual"][index - 1] for index in healthy["overflow_indices"]],
            [-2, -2, 1.875, 1.875, 1.875],
        )
        self.assertEqual(broken["mismatch_indices"], [1, 2, 23, 24, 25])
        self.assertEqual(
            [broken["actual"][index - 1] for index in broken["mismatch_indices"]],
            [1.125, 1.875, -2, -1.875, -1.125],
        )
        self.assertEqual(broken["direction_reversals"], 5)
        for index, overloaded in enumerate(healthy["overflow"]):
            if not overloaded:
                self.assertEqual(healthy["actual"][index], broken["actual"][index])
        inert = self.oracle(3, 2, 16, True)
        self.assertEqual(inert["overflow_indices"], [])
        self.assertEqual(inert["mismatch_indices"], [])
        self.assertEqual(inert["actual"], self.oracle()["actual"])

    def test_malformed_inputs_reject_and_valid_call_recovers(self):
        invalid_calls = (
            (-1, 2, 16, False),
            (9, 2, 16, False),
            (2.5, 2, 16, False),
            ([2, 3], 2, 16, False),
            (math.nan, 2, 16, False),
            (math.inf, 2, 16, False),
            (1 + 0j, 2, 16, False),
            (True, 2, 16, False),
            (3, -1, 16, False),
            (3, 5, 16, False),
            (3, 1.5, 16, False),
            (3, [1, 2], 16, False),
            (3, math.nan, 16, False),
            (3, math.inf, 16, False),
            (3, 1 + 0j, 16, False),
            (3, True, 16, False),
            (3, 2, 0, False),
            (3, 2, 26, False),
            (3, 2, 2.5, False),
            (3, 2, [2, 3], False),
            (3, 2, math.nan, False),
            (3, 2, math.inf, False),
            (3, 2, 1 + 0j, False),
            (3, 2, True, False),
            (3, 2, 16, 2),
            (3, 2, 16, 0.5),
            (3, 2, 16, [False, True]),
            (3, 2, 16, math.nan),
            (3, 2, 16, math.inf),
            (3, 2, 16, 1 + 0j),
        )
        expected = self.oracle()
        for arguments in invalid_calls:
            with self.subTest(arguments=arguments):
                with self.assertRaises(ValueError):
                    self.oracle(*arguments)
                self.assertEqual(self.oracle(), expected)

    def test_determinism_selected_view_isolation_and_fixed_allocation(self):
        baseline = self.oracle(6, 3, 11, False)
        for selected_sample in (1, 13, 25):
            current = self.oracle(6, 3, selected_sample, False)
            for field in (
                "rounded",
                "codes",
                "actual",
                "reference",
                "overflow",
                "errors",
            ):
                self.assertEqual(current[field], baseline[field])
        self.oracle(8, 0, 1, True)
        self.assertEqual(self.oracle(6, 3, 11, False), baseline)


if __name__ == "__main__":
    unittest.main()
