# Checks: Pipeline a Multiply-Accumulate

Ask and answer one prompt at a time.

## Observation check

For the two-stage dense baseline, identify the operand and product fractional-bit counts, product LSB, offered-product edges, accumulation edges, exact product codes, prefix-sum codes, and final scaled value. Why does token 1 update the accumulator at post-edge 3 rather than edge 1?

## Lever-isolation check

What changes when product-delay stages move from zero through four while input period remains one cycle? After resetting to two stages, what changes when input period moves from one through four cycles per product, and what numerical and ordering facts stay fixed?

## Limiting-case check

Explain why `L=0` makes the fault inert, why every healthy stage/period pair consumes exactly eight tokens in order, why the first accumulation edge stays 3 throughout the input-period sweep, and why completion edges are `[10,17,24,31]`.

## Broken-case check

At `L=2` and period one, why do broken valid pulses count two empty slots and six stale products before dropping token indices 7 and 8? Name the exact equal-delay assumption and explain why eight apparent valid events do not prove that eight correct products were accumulated.

## Interpretation and transfer check

Connect P05's binary-point contract to multiplying two signed `W=4`, `I=1` (sign excluded), `F=2` operands and to the conservative wide accumulator. Then distinguish a modeled product storage slot from a synthesized register or DSP slice, and name a feedback-retiming, overflow, reset, clock-rate, backpressure, or converter behavior this deterministic model assumes rather than proves.

## Executable check

Run in MATLAB:

```matlab
run_checks
```

All assertions must pass before completion. They cover exact operand/product/prefix codes, binary-point scaling, accepted numeric-class normalization, both independent sweeps, every healthy stage/period pair, per-stage schedule recurrence, zero-stage and sparse limits, broken token association and tail loss, malformed inputs, selected-view isolation, fixed resource bounds, deterministic recovery, and call isolation.

## Teach-back

In two sentences, answer: “What inputs, observable effects, and failure modes matter when you pipeline a Multiply-Accumulate?” Sentence one must explain how operand codes, binary points, product-delay stages, valid, token identity, and input spacing determine the healthy numerical timeline. Sentence two must name the equal-delay failure and connect its stale associations or dropped tail to the wrong final sum without relying on MATLAB syntax.
