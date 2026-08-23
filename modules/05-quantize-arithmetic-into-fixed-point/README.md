# P05 — Quantize Arithmetic into Fixed Point

**Track:** FPGA, Converter Interfaces, and High-Speed Data Paths  
**Phase 2:** Numeric hardware  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you quantize Arithmetic into Fixed Point?

## Computational mental model

A signed fixed-point word assigns meaning to each stored bit. This lesson uses one sign bit, `I` integer-magnitude bits, and `F` fractional bits. The least-significant-bit weight and total word length are

\[
\Delta=2^{-F},\qquad W=1+I+F.
\]

The healthy conversion rounds a sample to the nearest integer code, with exact half-LSB ties away from zero, then saturates that code into the signed two's-complement interval:

\[
c=\operatorname{sgn}(x)\left\lfloor |x|/\Delta+\tfrac12\right\rfloor,
\quad
\hat{x}=\Delta\min(\max(c,-2^{W-1}),2^{W-1}-1).
\]

The representable range is `[-2^I, 2^I - Delta]`. Inside that range the rounding error is bounded by half an LSB. Beyond it, saturation error grows with overload.

## Connection to P04

P04 stored a two-bit FSM state whose codes were symbolic labels. P05 keeps the same finite-code idea but assigns binary weights to the bits, so adjacent codes differ by one LSB and the endpoints define numerical range. A real datapath often uses a P04-style controller to decide when P05-style numeric codes are accepted or updated.

## Learner flow

1. Read the format, rounding, and saturation contract and make one prediction for the baseline.
2. Visualize the fixed 25-sample input/output mapping and its error trace.
3. Hold two integer-magnitude bits and sweep only fractional bits from zero through eight.
4. Explain why each added fractional bit halves the LSB and the in-range error bound while adding one word bit.
5. Reset to three fractional bits and sweep only integer-magnitude bits from zero through four.
6. Explain why range expands while the LSB stays fixed, eliminating overload without improving in-range resolution.
7. Replace saturation with wrapped overflow and diagnose the polarity reversals.
8. Run deterministic checks and give the teach-back in `checks.md`.

## Run the module

From the repository root, use MATLAB:

```matlab
launch_lesson("P05")
run_module_checks("P05")
```

Or enter this folder and run `experiment.m` one `%%` section at a time. Open `interactive.m` for bounded controls and linked sample-mapping/error views.

## Levers and observables

- `fractionBits` (`0..8`) changes LSB weight and precision; with integer bits fixed it also adds one word bit per step.
- `integerBits` (`0..4`, excluding sign) changes numerical range; with fractional bits fixed it leaves LSB weight unchanged.
- `selectedSample` (`1..25`) inspects input, scaled value, rounded code, output, error, and overflow status without changing the deterministic vector.
- `brokenWrap` is enabled in the UI only when the selected format overloads at least one sample. It violates the declared saturation policy by wrapping codes modulo the available code count.
- Views show the discrete input/output sample mapping in unitless normalized amplitude and quantization error by sample.
- Metrics report LSB, range, word length, in-range RMS/max error, overloads, saturation-reference mismatches, and direction reversals.

Word length and code count describe this teaching model's numeric format. They are not synthesis results or measured FPGA resources.

## Artifact and dependency contract

- `model.m` owns the deterministic vector, explicit code arithmetic, validation, healthy reference, and metrics without presentation.
- `experiment.m` owns the baseline, two isolated sweeps, labeled plots, and deliberately broken wrap case.
- `interactive.m` owns bounded `uifigure` controls and immediate sample-mapping/error feedback.
- `lesson.m`, `lesson.md`, and `walkthrough.md` own the concept-first sequence.
- `checks.md` and `run_checks.m` own interpretation and executable invariants.
- Dependency: P04. The implementation prefers base MATLAB and has no random, toolbox, external-file, network, process, asynchronous, or hardware dependency.

## Scope and limitations

Samples are deterministic normalized numbers, not measured converter data. The model defines one rounding and saturation policy; HDL languages, IP blocks, processors, and interfaces may choose different tie, resize, and overflow rules. It does not model pipeline latency, bit growth through multiplication, coefficient quantization, noise spectra, dither, synthesis, timing, power, or physical converter behavior. Wrapped overflow is a deterministic policy error relative to this lesson's saturation contract, not physical fault injection. MATLAB execution, figure rendering, UI behavior, numerical fidelity, and hardware behavior require separate evidence.
