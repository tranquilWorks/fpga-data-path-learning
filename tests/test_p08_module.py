from __future__ import annotations

import cmath
import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_FOLDER = ROOT / "modules/08-generate-a-numerically-controlled-oscillator"
GUIDING_QUESTION = (
    "What inputs, observable effects, and failure modes matter when you generate "
    "a Numerically Controlled Oscillator?"
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
TUNING_SWEEP = [0, 1, 64, 128, 256, 411, 512, 1024, 2047]


class P08ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "curriculum/modules.json").read_text(encoding="utf-8")
        )
        cls.module = next(
            module for module in cls.manifest["modules"] if module["id"] == "P08"
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
                "number": 8,
                "id": "P08",
                "title": "Generate a Numerically Controlled Oscillator",
                "guiding_question": GUIDING_QUESTION,
                "phase": 2,
                "phase_title": "Numeric hardware",
                "slug": "generate-a-numerically-controlled-oscillator",
                "folder": "modules/08-generate-a-numerically-controlled-oscillator",
                "implementation_batch": "P08",
                "prerequisites": ["P07"],
                "status": "implemented",
                "evidence_level": "simulated",
            },
        )
        p07 = next(
            module for module in self.manifest["modules"] if module["id"] == "P07"
        )
        self.assertEqual(p07["status"], "implemented")
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
            "p07",
            "phase accumulator",
            "tuning resolution",
            "lookup",
            "modulo",
            "sample zero",
            "100 mhz",
        ):
            self.assertIn(marker, lesson)
        for marker in ("learning cycle", "baseline", "lever 1", "lever 2", "mechanism first"):
            self.assertIn(marker, lesson)
        self.assertIn("make no second prediction", lesson)
        self.assertIn("make no second prediction", walkthrough)
        self.assertIn("one prompt at a time", checks)
        self.assertIn("limiting-case check", checks)
        self.assertIn("teach-back", checks)
        self.assertIn("two sentences", checks)
        for limitation in (
            "bram",
            "achieved timing",
            "amplitude quantization",
            "jitter",
            "phase noise",
            "bench",
        ):
            self.assertIn(limitation, lesson)

    def test_model_is_transparent_deterministic_bounded_and_presentation_free(self):
        source = self.read("model.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        for expression in (
            "accumulatorBits=12;",
            "phaseModulus=2^accumulatorBits;",
            "recordSampleCount=phaseModulus;",
            "sampleIndex=(0:recordSampleCount-1).';",
            "phaseTruncationFactor=2^discardedPhaseBits;",
            "effectiveTuningWord=floor(tuningWord/phaseTruncationFactor)*phaseTruncationFactor;",
            "referencePhaseCode=mod(initialPhaseCode+sampleIndex*tuningWord,phaseModulus);",
            "phaseCode=mod(initialPhaseCode+sampleIndex*effectiveTuningWord,phaseModulus);",
            "referenceLookupAddress=floor(referencePhaseCode/phaseTruncationFactor);",
            "lookupAddress=floor(phaseCode/phaseTruncationFactor);",
            "requestedFrequencyMHz=tuningWord*sampleClockMHz/phaseModulus;",
            "actualFrequencyMHz=effectiveTuningWord*sampleClockMHz/phaseModulus;",
            "spectralNumericalFloorDbc=-240;",
        ):
            self.assertIn(expression, compact)
        for transparent_operation in (
            "lookupCosineTable = cos(",
            "lookupSineTable = sin(",
            "referenceSpectrum = fft(",
            "spectrum = fft(",
        ):
            self.assertIn(transparent_operation, source)
        for field in (
            "referencePhaseCode",
            "phaseCode",
            "referencePhaseStepCode",
            "phaseStepCode",
            "referenceWrapCount",
            "wrapCount",
            "referenceWithinRecordWrapCount",
            "withinRecordWrapCount",
            "transitionCount",
            "withinRecordTransitionCount",
            "referenceTerminalNextPhaseCode",
            "terminalNextPhaseCode",
            "referenceLookupAddress",
            "lookupAddress",
            "phaseTruncationErrorDegrees",
            "requestedFrequencyMHz",
            "actualFrequencyMHz",
            "frequencyErrorKHz",
            "referenceAccumulatorPeriodSamples",
            "accumulatorPeriodSamples",
            "spectralNumericalFloorDbc",
            "spectralFloorLimited",
            "recordSfdrDb",
            "maxRecordSamples",
            "maxLookupEntries",
            "maxLookupPairValues",
        ):
            self.assertIn(field, source)
        for identifier in (
            "P08:InvalidTuningWord",
            "P08:InvalidPhaseAddressBits",
            "P08:InvalidInitialPhaseCode",
            "P08:InvalidBrokenIncrementTruncation",
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
            "dsp.",
            "comm.",
            "numerictype",
            "fimath",
            "fi(",
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
            "tuningWord=double(tuningWord);",
            "phaseAddressBits=double(phaseAddressBits);",
            "initialPhaseCode=double(initialPhaseCode);",
            "brokenIncrementTruncation=logical(brokenIncrementTruncation);",
        ):
            self.assertIn(conversion, compact_model)
        compact_checks = re.sub(r"\s+", "", self.read("run_checks.m")).replace(
            "...", ""
        )
        self.assertIn(
            "typedBaseline=model(uint16(411),uint8(8),uint16(0),uint8(0));",
            compact_checks,
        )
        self.assertIn("isequaln(typedBaseline,baseline)", compact_checks)
        self.assertIn("P08:NumericClassNormalization", self.read("run_checks.m"))

    def test_experiment_has_independent_sweeps_labels_metrics_and_broken_case(self):
        source = self.read("experiment.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "")
        self.assertGreaterEqual(source.count("%%"), 9)
        self.assertIn("sweep 1", lower)
        self.assertIn("sweep 2", lower)
        self.assertIn(
            "tuningWords=[016412825641151210242047];",
            compact,
        )
        self.assertIn("phaseAddressWidths=3:12;", compact)
        self.assertIn("model(tuningWords(sweepIndex),8,0,false)", compact)
        self.assertIn("model(411,phaseAddressWidths(sweepIndex),0,false)", compact)
        self.assertIn("tuning-word sweep must preserve lookup width", lower)
        self.assertIn("phase-address sweep must preserve full accumulator phase", lower)
        self.assertIn("deliberately broken case", lower)
        self.assertIn("healthy=model(411,8,0,false);", compact)
        self.assertIn("broken=model(411,8,0,true);", compact)
        self.assertIn("accumulate full precision", lower)
        self.assertIn("broken.effectiveTuningWord==400", compact)
        self.assertGreaterEqual(lower.count("drawnow"), 16)
        self.assertIn("one view at a time", lower)
        self.assertGreaterEqual(lower.count("xlabel("), 16)
        self.assertGreaterEqual(lower.count("ylabel("), 16)
        for unit_marker in (
            "[index]",
            "[unsigned 12-bit code]",
            "[degrees]",
            "[normalized amplitude]",
            "[mhz at assumed 100 mhz]",
            "[dbc]",
            "[phase entries]",
            "[samples]",
        ):
            self.assertIn(unit_marker, lower)
        for metric in (
            "frequency",
            "wrap",
            "period",
            "lookup",
            "phase error",
            "sfdr",
        ):
            self.assertIn(metric, lower)
        self.assertNotIn("close all", lower)

    def test_interactive_controls_are_bounded_model_backed_and_fault_safe(self):
        source = self.read("interactive.m")
        lower = source.lower()
        self.assertIn("modelFcn = @model", source)
        self.assertGreaterEqual(lower.count("uispinner("), 3)
        self.assertIn("uicheckbox(", lower)
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*0\s+2047\s*\]")
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*3\s+12\s*\]")
        self.assertRegex(source, r"'Limits'\s*,\s*\[\s*0\s+4095\s*\]")
        self.assertGreaterEqual(source.count("ValueChangedFcn"), 4)
        self.assertIn("mod(tuningWord,truncationFactor) == 0", source)
        clear_fault = source.index("faultCheckbox.Value = false")
        disable_fault = source.index("faultCheckbox.Enable = 'off'")
        self.assertLess(clear_fault, disable_fault)
        for phrase in (
            "k controls phase advance",
            "p controls lookup granularity",
            "frequency required/applied",
            "lookup entries",
            "phase error",
            "assumed",
            "not bram",
        ):
            self.assertIn(phrase, lower)
        self.assertIn("requestedFrequencyMHz", source)
        self.assertIn("actualFrequencyMHz", source)
        self.assertIn("referenceSpectrumDbcCentered", source)
        self.assertIn("spectrumDbcCentered", source)
        self.assertNotIn("close all", lower)

    def test_checks_cover_limits_fault_validation_recovery_and_resource_bounds(self):
        source = self.read("run_checks.m")
        lower = source.lower()
        compact = re.sub(r"\s+", "", source).replace("...", "").lower()
        self.assertGreaterEqual(lower.count("assert("), 30)
        self.assertIn("expectedfirstphasecode=[04118221233164420552466", compact)
        self.assertIn("tuningwords=[016412825641151210242047];", compact)
        self.assertIn("phaseaddresswidths=3:12;", compact)
        self.assertIn(
            "gridtuningwords=[0115161725525641151210242047];",
            compact,
        )
        for identifier in (
            "P08:BaselineRecurrence",
            "P08:BaselineLookup",
            "P08:BaselineFrequency",
            "P08:BaselineSpectrum",
            "P08:NumericClassNormalization",
            "P08:TuningSweep",
            "P08:TuningSweepIsolation",
            "P08:TuningPeriod",
            "P08:DcLimit",
            "P08:MinimumFrequencyLimit",
            "P08:QuarterRateLimit",
            "P08:HighestFrequencyLimit",
            "P08:AddressSweep",
            "P08:AddressSweepIsolation",
            "P08:FullAddressLimit",
            "P08:BrokenIncrement",
            "P08:BrokenFrequency",
            "P08:BrokenIsolation",
            "P08:BrokenInertLimits",
            "P08:HealthyGrid",
            "P08:BrokenGridActive",
            "P08:ResourceBound",
            "P08:InitialPhaseIsolation",
            "P08:InitialPhaseWrapPartition",
            "P08:DeterminismRecovery",
            "P08:InvalidTuningWord",
            "P08:InvalidPhaseAddressBits",
            "P08:InvalidInitialPhaseCode",
            "P08:InvalidBrokenIncrementTruncation",
        ):
            self.assertIn(identifier.lower(), lower)
        self.assertIn("p08 checks passed", lower)

    def test_p08_text_files_have_exactly_one_terminal_newline(self):
        for name in REQUIRED_ARTIFACTS:
            with self.subTest(artifact=name):
                data = (MODULE_FOLDER / name).read_bytes()
                self.assertTrue(data.endswith(b"\n"))
                self.assertFalse(data.endswith(b"\n\n"))
                self.assertNotIn(b"\r", data)


class P08IndependentOracleTests(unittest.TestCase):
    @staticmethod
    def oracle(
        tuning_word: int = 411,
        phase_address_bits: int = 8,
        initial_phase: int = 0,
        broken_increment: bool = False,
    ):
        if type(tuning_word) is not int or not 0 <= tuning_word <= 2047:
            raise ValueError("tuning_word")
        if type(phase_address_bits) is not int or not 3 <= phase_address_bits <= 12:
            raise ValueError("phase_address_bits")
        if type(initial_phase) is not int or not 0 <= initial_phase <= 4095:
            raise ValueError("initial_phase")
        valid_flag = type(broken_increment) is bool or (
            type(broken_increment) is int and broken_increment in (0, 1)
        )
        if not valid_flag:
            raise ValueError("broken_increment")
        broken_increment = bool(broken_increment)

        modulus = 4096
        sample_count = 4096
        truncation_factor = 1 << (12 - phase_address_bits)
        entries = 1 << phase_address_bits
        effective_word = tuning_word
        if broken_increment:
            effective_word = (tuning_word // truncation_factor) * truncation_factor
        discarded_word = tuning_word - effective_word
        reference_phase = [
            (initial_phase + index * tuning_word) % modulus
            for index in range(sample_count)
        ]
        phase = [
            (initial_phase + index * effective_word) % modulus
            for index in range(sample_count)
        ]
        reference_address = [value // truncation_factor for value in reference_phase]
        address = [value // truncation_factor for value in phase]
        phase_error_codes = [
            lookup * truncation_factor - value
            for lookup, value in zip(address, phase)
        ]
        phase_error_degrees = [value * 360 / modulus for value in phase_error_codes]
        table = [
            cmath.exp(2j * math.pi * address_index / entries)
            for address_index in range(entries)
        ]
        output = [table[value] for value in address]
        ideal_output = [
            cmath.exp(2j * math.pi * value / modulus) for value in phase
        ]
        waveform_rms_error = math.sqrt(
            sum(abs(actual - ideal) ** 2 for actual, ideal in zip(output, ideal_output))
            / sample_count
        )
        wraps = sum(value + effective_word >= modulus for value in phase)
        reference_wraps = sum(value + tuning_word >= modulus for value in reference_phase)
        within_record_wraps = sum(
            current < previous for previous, current in zip(phase, phase[1:])
        )
        reference_within_record_wraps = sum(
            current < previous
            for previous, current in zip(reference_phase, reference_phase[1:])
        )
        terminal_next_phase = (phase[-1] + effective_word) % modulus
        reference_terminal_next_phase = (
            reference_phase[-1] + tuning_word
        ) % modulus
        terminal_wrap = phase[-1] + effective_word >= modulus
        reference_terminal_wrap = reference_phase[-1] + tuning_word >= modulus
        period = 1 if effective_word == 0 else modulus // math.gcd(modulus, effective_word)
        reference_period = (
            1 if tuning_word == 0 else modulus // math.gcd(modulus, tuning_word)
        )
        return {
            "modulus": modulus,
            "sample_count": sample_count,
            "truncation_factor": truncation_factor,
            "entries": entries,
            "effective_word": effective_word,
            "discarded_word": discarded_word,
            "fault_active": broken_increment and discarded_word != 0,
            "reference_phase": reference_phase,
            "phase": phase,
            "reference_address": reference_address,
            "address": address,
            "phase_error_codes": phase_error_codes,
            "phase_error_degrees": phase_error_degrees,
            "maximum_phase_error_degrees": max(map(abs, phase_error_degrees)),
            "rms_phase_error_degrees": math.sqrt(
                sum(value * value for value in phase_error_degrees) / sample_count
            ),
            "output": output,
            "waveform_rms_error": waveform_rms_error,
            "reference_wraps": reference_wraps,
            "wraps": wraps,
            "reference_within_record_wraps": reference_within_record_wraps,
            "within_record_wraps": within_record_wraps,
            "transition_count": sample_count,
            "within_record_transition_count": sample_count - 1,
            "reference_terminal_next_phase": reference_terminal_next_phase,
            "terminal_next_phase": terminal_next_phase,
            "reference_terminal_wrap": reference_terminal_wrap,
            "terminal_wrap": terminal_wrap,
            "reference_period": reference_period,
            "period": period,
            "requested_frequency_mhz": tuning_word * 100 / modulus,
            "actual_frequency_mhz": effective_word * 100 / modulus,
            "frequency_error_khz": (effective_word - tuning_word) * 100000 / modulus,
            "carrier_bin": effective_word,
            "reference_carrier_bin": tuning_word,
            "record_values": len(phase),
            "lookup_pair_values": 2 * entries,
        }

    @staticmethod
    def dft_magnitude(values, bin_number: int) -> float:
        sample_count = len(values)
        total = sum(
            value * cmath.exp(-2j * math.pi * bin_number * index / sample_count)
            for index, value in enumerate(values)
        )
        return abs(total / sample_count)

    @staticmethod
    def fft(values):
        """Independent radix-2 FFT used only as a test oracle."""
        count = len(values)
        if count == 0 or count & (count - 1):
            raise ValueError("FFT length must be a nonzero power of two")
        transformed = [complex(value) for value in values]
        reversed_index = 0
        for index in range(1, count):
            bit = count >> 1
            while reversed_index & bit:
                reversed_index ^= bit
                bit >>= 1
            reversed_index ^= bit
            if index < reversed_index:
                transformed[index], transformed[reversed_index] = (
                    transformed[reversed_index],
                    transformed[index],
                )
        group_size = 2
        while group_size <= count:
            group_rotation = cmath.exp(-2j * math.pi / group_size)
            half_group = group_size // 2
            for group_start in range(0, count, group_size):
                rotation = 1 + 0j
                for offset in range(half_group):
                    even_index = group_start + offset
                    odd_index = even_index + half_group
                    odd = rotation * transformed[odd_index]
                    even = transformed[even_index]
                    transformed[even_index] = even + odd
                    transformed[odd_index] = even - odd
                    rotation *= group_rotation
            group_size *= 2
        return transformed

    @classmethod
    def spectral_metrics(cls, values, carrier_bin: int):
        spectrum = cls.fft(values)
        carrier = abs(spectrum[carrier_bin])
        largest_spur = max(
            abs(value) for index, value in enumerate(spectrum) if index != carrier_bin
        )
        floor_dbc = -240
        floor_magnitude = carrier * 10 ** (floor_dbc / 20)
        floor_limited = largest_spur <= floor_magnitude
        sfdr_db = (
            math.inf
            if floor_limited
            else 20 * math.log10(carrier / largest_spur)
        )
        return sfdr_db, floor_limited, largest_spur, floor_magnitude

    def test_exact_baseline_recurrence_frequency_lookup_and_errors(self):
        result = self.oracle()
        self.assertEqual(
            result["phase"][:12],
            [0, 411, 822, 1233, 1644, 2055, 2466, 2877, 3288, 3699, 14, 425],
        )
        self.assertEqual(
            result["address"][:12],
            [0, 25, 51, 77, 102, 128, 154, 179, 205, 231, 0, 26],
        )
        self.assertEqual(result["reference_phase"], result["phase"])
        self.assertEqual(result["wraps"], 411)
        self.assertEqual(result["within_record_wraps"], 410)
        self.assertEqual(result["transition_count"], 4096)
        self.assertEqual(result["within_record_transition_count"], 4095)
        self.assertEqual(result["terminal_next_phase"], 0)
        self.assertEqual(result["period"], 4096)
        self.assertEqual(result["entries"], 256)
        self.assertEqual(result["truncation_factor"], 16)
        self.assertEqual(result["requested_frequency_mhz"], 10.0341796875)
        self.assertEqual(result["actual_frequency_mhz"], 10.0341796875)
        self.assertEqual(result["frequency_error_khz"], 0)
        self.assertEqual(result["maximum_phase_error_degrees"], 15 * 360 / 4096)
        self.assertAlmostEqual(
            result["rms_phase_error_degrees"],
            math.sqrt(sum(value * value for value in range(16)) / 16) * 360 / 4096,
        )
        carrier = self.dft_magnitude(result["output"], 411)
        wrong_bin = self.dft_magnitude(result["output"], 400)
        self.assertGreater(carrier, 0.99)
        self.assertGreater(carrier, 100 * wrong_bin)
        sfdr_db, floor_limited, largest_spur, floor_magnitude = (
            self.spectral_metrics(result["output"], 411)
        )
        self.assertFalse(floor_limited)
        self.assertGreater(largest_spur, floor_magnitude)
        self.assertAlmostEqual(sfdr_db, 48.07535746411204, places=10)

    def test_tuning_sweep_obeys_frequency_wrap_period_and_isolation(self):
        results = [self.oracle(value, 8, 0, False) for value in TUNING_SWEEP]
        self.assertEqual(
            [result["actual_frequency_mhz"] for result in results],
            [value * 100 / 4096 for value in TUNING_SWEEP],
        )
        self.assertEqual([result["wraps"] for result in results], TUNING_SWEEP)
        self.assertEqual(
            [result["within_record_wraps"] for result in results],
            [0, 0, 63, 127, 255, 410, 511, 1023, 2046],
        )
        self.assertEqual(
            [result["period"] for result in results],
            [1, 4096, 64, 32, 16, 4096, 8, 4, 4096],
        )
        self.assertEqual([result["entries"] for result in results], [256] * 9)
        self.assertEqual([result["record_values"] for result in results], [4096] * 9)
        for tuning_word, result in zip(TUNING_SWEEP, results):
            self.assertEqual(
                result["phase"],
                [(index * tuning_word) % 4096 for index in range(4096)],
            )

    def test_address_sweep_changes_lookup_error_not_full_phase_or_frequency(self):
        results = [self.oracle(411, bits, 0, False) for bits in range(3, 13)]
        self.assertEqual([result["entries"] for result in results], [2**bits for bits in range(3, 13)])
        baseline_phase = results[0]["phase"]
        for bits, result in zip(range(3, 13), results):
            factor = 1 << (12 - bits)
            expected_maximum = (factor - 1) * 360 / 4096
            expected_rms = (
                math.sqrt(sum(value * value for value in range(factor)) / factor)
                * 360
                / 4096
            )
            self.assertEqual(result["phase"], baseline_phase)
            self.assertEqual(result["actual_frequency_mhz"], 411 * 100 / 4096)
            self.assertAlmostEqual(result["maximum_phase_error_degrees"], expected_maximum)
            self.assertAlmostEqual(result["rms_phase_error_degrees"], expected_rms)
            self.assertLessEqual(result["lookup_pair_values"], 8192)
        maximum_errors = [result["maximum_phase_error_degrees"] for result in results]
        waveform_errors = [result["waveform_rms_error"] for result in results]
        self.assertTrue(all(a >= b for a, b in zip(maximum_errors, maximum_errors[1:])))
        self.assertTrue(all(a >= b for a, b in zip(waveform_errors, waveform_errors[1:])))
        self.assertEqual(results[-1]["phase_error_codes"], [0] * 4096)
        self.assertEqual(results[-1]["waveform_rms_error"], 0)
        sfdr_db, floor_limited, largest_spur, floor_magnitude = (
            self.spectral_metrics(results[-1]["output"], 411)
        )
        self.assertTrue(floor_limited)
        self.assertLessEqual(largest_spur, floor_magnitude)
        self.assertTrue(math.isinf(sfdr_db))

    def test_dc_quarter_rate_and_high_frequency_limits(self):
        dc = self.oracle(0, 8, 777, False)
        self.assertEqual(dc["phase"], [777] * 4096)
        self.assertEqual(dc["wraps"], 0)
        self.assertEqual(dc["within_record_wraps"], 0)
        self.assertEqual(dc["period"], 1)
        self.assertTrue(all(value == dc["output"][0] for value in dc["output"]))
        minimum = self.oracle(1, 8, 0, False)
        self.assertEqual(minimum["actual_frequency_mhz"], 100 / 4096)
        self.assertEqual(
            (minimum["wraps"], minimum["within_record_wraps"], minimum["period"]),
            (1, 0, 4096),
        )
        quarter = self.oracle(1024, 8, 0, False)
        self.assertEqual(quarter["phase"][:8], [0, 1024, 2048, 3072] * 2)
        self.assertEqual((quarter["actual_frequency_mhz"], quarter["period"]), (25, 4))
        expected_quadrature = [1, 1j, -1, -1j]
        for actual, expected in zip(quarter["output"][:4], expected_quadrature):
            self.assertAlmostEqual(abs(actual - expected), 0)
        highest = self.oracle(2047, 8, 0, False)
        self.assertLess(highest["actual_frequency_mhz"], 50)
        self.assertEqual(highest["carrier_bin"], 2047)

    def test_broken_increment_has_exact_frequency_period_and_spectral_symptom(self):
        healthy = self.oracle(411, 8, 0, False)
        broken = self.oracle(411, 8, 0, True)
        self.assertEqual(broken["effective_word"], 400)
        self.assertEqual(broken["discarded_word"], 11)
        self.assertTrue(broken["fault_active"])
        self.assertEqual(broken["actual_frequency_mhz"], 9.765625)
        self.assertEqual(broken["frequency_error_khz"], -268.5546875)
        self.assertEqual((broken["reference_wraps"], broken["wraps"]), (411, 400))
        self.assertEqual(
            (
                broken["reference_within_record_wraps"],
                broken["within_record_wraps"],
            ),
            (410, 399),
        )
        self.assertEqual(
            (
                broken["reference_terminal_next_phase"],
                broken["terminal_next_phase"],
            ),
            (0, 0),
        )
        self.assertEqual((broken["reference_period"], broken["period"]), (4096, 256))
        self.assertEqual(broken["reference_phase"], healthy["reference_phase"])
        self.assertNotEqual(broken["phase"], healthy["phase"])
        correct_bin = self.dft_magnitude(broken["output"], 400)
        requested_bin = self.dft_magnitude(broken["output"], 411)
        self.assertGreater(correct_bin, 0.99)
        self.assertGreater(correct_bin, 100 * requested_bin)

    def test_inert_fault_limits_and_representative_grid_are_bounded(self):
        for arguments in ((512, 8, 0), (0, 3, 901), (411, 12, 0)):
            healthy = self.oracle(*arguments, False)
            broken = self.oracle(*arguments, True)
            with self.subTest(arguments=arguments):
                self.assertFalse(broken["fault_active"])
                self.assertEqual(broken["phase"], healthy["phase"])
                self.assertEqual(broken["output"], healthy["output"])
                self.assertEqual(
                    broken["actual_frequency_mhz"], healthy["actual_frequency_mhz"]
                )

        grid_words = [0, 1, 15, 16, 17, 255, 256, 411, 512, 1024, 2047]
        for tuning_word in grid_words:
            for bits in range(3, 13):
                healthy = self.oracle(tuning_word, bits, 4095, False)
                broken = self.oracle(tuning_word, bits, 4095, True)
                factor = 1 << (12 - bits)
                expected_effective = (tuning_word // factor) * factor
                with self.subTest(tuning_word=tuning_word, bits=bits):
                    self.assertEqual(healthy["effective_word"], tuning_word)
                    self.assertEqual(broken["effective_word"], expected_effective)
                    self.assertEqual(broken["reference_phase"], healthy["reference_phase"])
                    self.assertLessEqual(broken["actual_frequency_mhz"], broken["requested_frequency_mhz"])
                    self.assertEqual(healthy["record_values"], 4096)
                    self.assertLessEqual(healthy["entries"], 4096)
                    self.assertLessEqual(healthy["lookup_pair_values"], 8192)
                    self.assertTrue(all(0 <= value < healthy["entries"] for value in healthy["address"]))
                    if tuning_word % factor == 0:
                        self.assertFalse(broken["fault_active"])
                        self.assertEqual(broken["phase"], healthy["phase"])
                    else:
                        self.assertTrue(broken["fault_active"])
                        self.assertLess(
                            broken["actual_frequency_mhz"],
                            broken["requested_frequency_mhz"],
                        )

    def test_malformed_inputs_reject_and_valid_call_recovers(self):
        invalid_calls = (
            (-1, 8, 0, False),
            (2048, 8, 0, False),
            (411.5, 8, 0, False),
            ([411, 412], 8, 0, False),
            (math.nan, 8, 0, False),
            (math.inf, 8, 0, False),
            (411 + 1j, 8, 0, False),
            (True, 8, 0, False),
            (411, 2, 0, False),
            (411, 13, 0, False),
            (411, 8.5, 0, False),
            (411, [8, 9], 0, False),
            (411, math.nan, 0, False),
            (411, math.inf, 0, False),
            (411, 8 + 1j, 0, False),
            (411, True, 0, False),
            (411, 8, -1, False),
            (411, 8, 4096, False),
            (411, 8, 0.5, False),
            (411, 8, [0, 1], False),
            (411, 8, math.nan, False),
            (411, 8, math.inf, False),
            (411, 8, 1j, False),
            (411, 8, True, False),
            (411, 8, 0, 2),
            (411, 8, 0, 0.5),
            (411, 8, 0, [False, True]),
            (411, 8, 0, math.nan),
            (411, 8, 0, math.inf),
            (411, 8, 0, 1 + 1j),
        )
        expected = self.oracle()
        for arguments in invalid_calls:
            with self.subTest(arguments=arguments):
                with self.assertRaises(ValueError):
                    self.oracle(*arguments)
                self.assertEqual(self.oracle(), expected)

    def test_initial_phase_isolation_determinism_and_recovery(self):
        zero_phase = self.oracle(411, 8, 0, False)
        quarter_turn = self.oracle(411, 8, 1024, False)
        self.assertEqual(
            quarter_turn["phase"],
            [(value + 1024) % 4096 for value in zero_phase["phase"]],
        )
        for field in (
            "effective_word",
            "entries",
            "requested_frequency_mhz",
            "actual_frequency_mhz",
            "reference_wraps",
            "wraps",
            "reference_period",
            "period",
            "record_values",
            "lookup_pair_values",
        ):
            self.assertEqual(quarter_turn[field], zero_phase[field])
        self.oracle(2047, 3, 4095, True)
        self.assertEqual(self.oracle(411, 8, 0, False), zero_phase)

    def test_initial_phase_partitions_stored_and_terminal_wraps(self):
        for initial_phase in (0, 399, 400, 410, 411, 1024, 4095):
            result = self.oracle(411, 8, initial_phase, True)
            expected_reference_terminal_wrap = initial_phase < 411
            expected_terminal_wrap = initial_phase < 400
            with self.subTest(initial_phase=initial_phase):
                self.assertEqual(result["reference_wraps"], 411)
                self.assertEqual(result["wraps"], 400)
                self.assertEqual(
                    result["reference_terminal_wrap"],
                    expected_reference_terminal_wrap,
                )
                self.assertEqual(result["terminal_wrap"], expected_terminal_wrap)
                self.assertEqual(
                    result["reference_within_record_wraps"],
                    411 - expected_reference_terminal_wrap,
                )
                self.assertEqual(
                    result["within_record_wraps"],
                    400 - expected_terminal_wrap,
                )
                self.assertEqual(
                    result["reference_within_record_wraps"]
                    + result["reference_terminal_wrap"],
                    result["reference_wraps"],
                )
                self.assertEqual(
                    result["within_record_wraps"] + result["terminal_wrap"],
                    result["wraps"],
                )
                self.assertEqual(
                    result["reference_terminal_next_phase"], initial_phase
                )
                self.assertEqual(result["terminal_next_phase"], initial_phase)


if __name__ == "__main__":
    unittest.main()
