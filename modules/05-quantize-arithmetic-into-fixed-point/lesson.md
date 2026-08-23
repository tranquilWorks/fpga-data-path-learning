# Lesson: Quantize Arithmetic into Fixed Point

## Guiding question

What inputs, observable effects, and failure modes matter when you quantize Arithmetic into Fixed Point?

## Mental model

A fixed-point word is an integer code plus an agreed binary-point position. With one sign bit, `I` integer-magnitude bits, and `F` fractional bits,

\[
W=1+I+F,\qquad \Delta=2^{-F},\qquad
x_{min}=-2^I,\quad x_{max}=2^I-\Delta.
\]

`Delta` is one LSB. The model first rounds `x/Delta` to the nearest integer code, with exact half-LSB ties away from zero. It then saturates that code to the signed two's-complement endpoints and scales back by `Delta`. For every sample whose rounded code is inside the format,

\[
e=\hat{x}-x,\qquad |e|\leq\Delta/2.
\]

Overflow is a different mechanism: once the requested rounded code is outside the endpoint codes, saturation pins the result and its error is no longer limited to half an LSB.

## Connection to P04

P04 used a finite set of registered symbolic FSM codes as labels for `IDLE`, `WAIT`, `DONE`, and `TIMEOUT`; numerical distance between those labels had no meaning. P05 turns them into weighted numeric codes by giving each bit a positional value. Consecutive codes now differ by one LSB, and the finite number of codes creates both a resolution and a range boundary. A P04-style controller can govern when these numeric datapath values are captured, but it does not change their fixed-point interpretation.

## Learning cycle

Read the format contract, visualize the baseline, move one lever, inspect the changed view, and then read the mechanism-first explanation. Reset before moving the second lever so precision and range remain distinct.

## One prediction before the baseline

The baseline uses two integer-magnitude bits and three fractional bits, so `Delta = 0.125` and the range is `[-4, 3.875]`. Predict the nearest output for input `0.31`. Then inspect the baseline once. Make no second prediction; subsequent prompts ask you to observe and explain.

## Baseline

The 25 sorted samples include ordinary in-range values and exact half-LSB ties. Every sample fits the six-bit baseline, so each output marker lands on its nearest representable code. The maximum absolute error is exactly `0.0625`, half an LSB. This clean discrete mapping keeps ordinary quantization separate from the overload introduced by the range sweep.

The unused negative endpoint is `-4`, while the positive endpoint is `3.875`. The negative side has one extra code because signed two's-complement codes run from `-2^(W-1)` through `2^(W-1)-1`.

## Lever 1: fractional bits

Hold integer-magnitude bits at two so all 25 samples fit, then sweep fractional bits from zero through eight. LSB values become `1, 1/2, 1/4, ..., 1/256`; total word lengths become three through eleven bits. The fixed vector never overloads in this sweep.

Mechanism first: adding one fractional bit doubles the number of code steps per unit and halves the half-LSB error bound. It does not increase the negative power-of-two range boundary. The plotted in-range RMS error falls for this vector because the discrete sample mapping follows the original values more closely.

## Lever 2: integer-magnitude bits

Reset fractional bits to three, fixing `Delta = 0.125`, then sweep integer-magnitude bits from zero through four. Overload counts are `[13, 5, 0, 0, 0]`. Once two integer-magnitude bits are available, every sample fits; adding still more range does not change any quantized result for this fixed vector.

Mechanism first: an integer bit doubles the endpoint scale and adds codes outside the old range. Because the binary-point position did not move, it does not change LSB spacing or in-range quantization precision.

## Deliberately broken case

Return to one integer-magnitude bit and three fractional bits, but replace saturation with modulo wrapping. A requested code outside `[-16, 15]` discards its high-order overflow information and re-enters the code interval from the opposite side. The five overloaded samples become five reference mismatches and five direction reversals: large positive inputs become negative outputs and large negative inputs become positive outputs.

The violated assumption is exact: this datapath contract requires saturation at overflow. Wrap is not universally invalid—some systems deliberately specify it—but silently substituting it here creates a recognizable, large discontinuity at the endpoints.

## Common mistakes

- Calling fractional bits “decimal places”; each bit changes a binary power-of-two weight.
- Counting the sign bit as an integer-magnitude bit in this lesson's format notation.
- Treating quantization error and overflow error as the same bounded effect.
- Assuming positive and negative endpoints are symmetric in signed two's complement.
- Assuming a language cast, IP block, or HDL resize uses this lesson's tie and overflow policies without checking.
- Calling modeled word length or code count a synthesis or physical-resource result.
- Inferring converter noise, spectral behavior, timing closure, or physical accuracy from deterministic normalized samples.

## Completion standard

Run `run_checks.m`, answer `checks.md` one prompt at a time, diagnose the wrap symptom, and give the requested two-sentence teach-back without explaining MATLAB syntax.
