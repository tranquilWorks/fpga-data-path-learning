# P06 — Pipeline a Multiply-Accumulate

**Track:** FPGA, Converter Interfaces, and High-Speed Data Paths  
**Phase 2:** Numeric hardware  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you pipeline a Multiply-Accumulate?

## Computational mental model

A multiply-accumulate consumes an ordered token stream. Token `k` carries an operand code, a coefficient code, and a valid bit. This lesson uses signed operands with `W=4`, `I=1` integer-magnitude bit excluding sign, and `F=2` fractional bits (often called Q1.2). Each operand LSB is `2^-2`, and the exact raw product has four fractional bits:

\[
p_{code}[k]=x_{code}[k]h_{code}[k],\qquad
p[k]=2^{-4}p_{code}[k].
\]

`L` counts only registered product-delay stages before the accumulator. Product data, valid, and token identity must traverse the same `L` cycle slots. When delayed valid is true, the deliberately wide accumulator updates as

\[
A_{code}[c]=A_{code}[c-1]+v_{in}[c-L]p_{code}[c-L],\qquad
A[c]=2^{-4}A_{code}[c],
\]

where indices `c-L <= 0` are invalid reset-fill slots.

Rows are post-edge observations. A product offered before edge `k` updates the accumulator after edge `k+L`. The accumulator update is that observation; this schedule model does not add a separate adder-register latency. `L=0` is the direct-product limiting case.

## Connection to P05

P05 established that a code is meaningless without its binary point and overflow policy. P06 preserves that contract through multiplication: two operands with two fractional bits create a product and accumulator with four fractional bits. The model declares a conservative 11-bit accumulator for the eight-product sequence; the observed trace itself needs six signed bits. Arithmetic is not finitely resized, rounded, saturated, or wrapped. That isolates pipeline scheduling from P05 quantization effects.

## Deterministic baseline

The eight operand-code pairs are

```text
x_code = [ 3, -2,  5, 1, -4,  6, -1, 4]
h_code = [ 2,  4, -1, 3,  2, -2,  5, 5]
p_code = [ 6, -8, -5, 3, -8,-12, -5,20]
```

Their exact sum is code `-9`, or `-9/16 = -0.5625`. With two product stages and one offered token per cycle, token 1 accumulates at edge 3 and token 8 completes at edge 10. The healthy sum is invariant to every exposed stage count and input period.

## Learner flow

1. Read the binary-point and post-edge timing contract, then make one prediction for the two-stage baseline.
2. Visualize offered products, delayed products, valid timing, and the running accumulator.
3. Hold input period at one cycle and sweep product stages from zero through four.
4. Explain why observation time and modeled storage change while product order and the final sum do not.
5. Reset to two product stages and sweep input period from one through four cycles per product.
6. Explain why bubbles stretch completion time without changing the ordered arithmetic.
7. Bypass the valid/token delay while leaving product data registered; diagnose empty early accumulations, stale token associations, and the dropped tail products.
8. Run deterministic checks and give the teach-back in `checks.md`.

## Run the module

From the repository root, use MATLAB:

```matlab
launch_lesson("P06")
run_module_checks("P06")
```

Or enter this folder and run `experiment.m` one `%%` section at a time. Open `interactive.m` for bounded controls and linked product-schedule/accumulator views.

## Levers and observables

- `pipelineStages` (`0..4`) changes the registered product delay, first/final accumulation edges, and modeled product/valid storage slots. It does not claim a clock-rate or synthesis benefit.
- `inputPeriod` (`1..4` cycles/product) changes the spacing between offered tokens and therefore between healthy accumulation events.
- `selectedCycle` inspects the current bounded timeline without changing any calculation.
- `brokenValidAlignment` is available only when at least one product register exists. It lets valid and token identity bypass all product-delay stages, making those labels untrustworthy.
- Views use clock edges in cycles, products in unitless product value, valid as binary rows, and accumulated values in unitless amplitude.
- Metrics report first/final accumulation edge, final code/value, dropped token identities, schedule mismatches, product LSB, trace code range, six-bit trace minimum, and conservative 11-bit modeled accumulator width.

Invalid bubble slots deliberately carry the legal nonzero diagnostic product code `-56`. Their data is meaningless because valid is false, and the accumulator must ignore it. This makes accidental bubble accumulation observable instead of letting zero-filled bubbles hide the error.

Modeled stage slots and word length describe this deterministic schedule and numeric contract. They are not synthesized registers, DSP slices, logic cells, achieved clock rate, timing closure, power, or measured FPGA utilization.

## Artifact and dependency contract

- `model.m` owns deterministic codes, per-cycle product/valid/token movement, accumulation, validation, and metrics without presentation.
- `experiment.m` owns the baseline, two isolated sweeps, labeled plots, and deliberately broken alignment case.
- `interactive.m` owns bounded `uifigure` controls and immediate schedule/result feedback.
- `lesson.m`, `lesson.md`, and `walkthrough.md` own the concept-first sequence.
- `checks.md` and `run_checks.m` own interpretation and executable invariants.
- Dependency: P05. The implementation prefers base MATLAB and has no random, toolbox, external-file, network, process, asynchronous, or hardware dependency.

## Scope and limitations

This is a cycle-level teaching model, not HDL, gate-level, timing, or physical simulation. It models only feed-forward product-delay registers and an exact wide accumulator; it does not retime or pipeline the feedback adder, predict a critical path, prove an initiation rate, model reset protocols, truncate products, overflow the accumulator, share multipliers, or estimate resources. The fixed codes are synthetic rather than measured converter samples. The broken case is a deterministic control-alignment error, not physical fault injection. MATLAB execution, figure rendering, UI behavior, numerical fidelity, synthesis, timing, bench, HIL, and field behavior require separate evidence.
