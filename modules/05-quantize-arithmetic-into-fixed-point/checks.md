# Checks: Quantize Arithmetic into Fixed Point

Ask and answer one prompt at a time.

## Observation check

For the overflow-free baseline, identify sign, integer-magnitude, and fractional bit counts; LSB weight; endpoint values; and the zero overload count. Why is the positive endpoint `3.875` while the negative endpoint is `-4`?

## Lever-isolation check

What changes when fractional bits move from zero through eight while integer-magnitude bits remain two? After resetting fractional bits to three, what changes when integer-magnitude bits move from zero through four, and what precision facts stay fixed?

## Limiting-case check

Explain why zero fractional bits give an LSB of one, why eight give `1/256`, why every in-range nearest-rounded result stays within half an LSB, and why adding range beyond two integer-magnitude bits leaves this fixed input vector unchanged.

## Broken-case check

At the deliberately narrowed `I=1, F=3` format, why do the five overloaded samples saturate in the healthy path but reverse direction in the wrapped path? Name the exact overflow-policy assumption and the recognizable endpoint-discontinuity symptom.

## Interpretation and transfer check

Explain how P04's finite symbolic codes differ from P05's weighted numeric codes. Name one later arithmetic block that needs an explicit binary point, then name a tie-rule, resize, synthesis, converter, or spectral fact this deterministic model assumes rather than proves.

## Executable check

Run in MATLAB:

```matlab
run_checks
```

All assertions must pass before completion. They cover the exact baseline vector and codes, half-LSB ties, endpoint asymmetry, accepted numeric-class normalization, two independent sweeps, the complete 45-format healthy grid, saturation and wrap behavior, inert fault limits, malformed inputs, selected-view isolation, fixed resource bounds, deterministic recovery, and call isolation.

## Teach-back

In two sentences, answer: “What inputs, observable effects, and failure modes matter when you quantize Arithmetic into Fixed Point?” Sentence one must explain how integer and fractional bits set range and LSB precision under the declared rounding rule. Sentence two must distinguish bounded in-range quantization error from saturation overload and the broken wrap symptom.
