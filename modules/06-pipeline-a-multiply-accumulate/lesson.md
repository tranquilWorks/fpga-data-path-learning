# Lesson: Pipeline a Multiply-Accumulate

## Guiding question

What inputs, observable effects, and failure modes matter when you pipeline a Multiply-Accumulate?

## Mental model

A multiply-accumulate is numerical state driven by an ordered token stream. Each token needs three things to stay associated:

- product data;
- a valid bit saying whether this cycle carries a real product;
- token identity, which lets us verify that the right valid bit names the right data.

The deterministic operands are signed codes with `W=4`, `I=1` integer-magnitude bit excluding sign, and `F=2` fractional bits (often called Q1.2). P05's binary-point rule therefore gives

\[
F_p=F_x+F_h=2+2=4,
\qquad p_{code}[k]=x_{code}[k]h_{code}[k],
\qquad p[k]=2^{-4}p_{code}[k].
\]

The accumulator keeps the same four fractional bits and is deliberately wide enough to avoid overflow:

\[
A_{code}[c]=A_{code}[c-1]+v_{in}[c-L]p_{code}[c-L],
\]

with indices `c-L <= 0` treated as invalid reset-fill slots.

Here `L` counts only product-delay registers before the accumulator. Every row is a post-edge observation just after its numbered edge. A product offered before edge `k` updates the accumulator after edge `k+L`; there is no separately modeled adder-register delay. At `L=0`, the product reaches the accumulator directly on the offered edge.

## Connection to P05

P05 showed that fractional-bit placement determines an LSB and that overflow policy must be explicit. P06 preserves those numerical meanings instead of silently converting back to arbitrary floating-point samples: two operands with `F=2` produce a product-code LSB of `1/16`, and every accumulated code is scaled by that same LSB. The model declares a conservative 11-bit accumulator for eight full-width product codes; this particular trace needs only six signed bits. No finite resize is applied, so any wrong answer in the broken case comes from scheduling and alignment rather than rounding, saturation, or wrap.

## Learning cycle

Read the data-and-valid contract, visualize the baseline, move one lever, inspect the changed view, and then read the mechanism-first explanation. Reset before moving the second lever so product-register delay and offered-token spacing remain distinct.

## One prediction before the baseline

The baseline offers token 1 before edge 1 and places two product registers before the accumulator. Predict the edge on which that product first updates the sum. Then inspect the baseline once. Make no second prediction; subsequent prompts ask you to observe and explain.

## Baseline

The exact product codes are `[6,-8,-5,3,-8,-12,-5,20]`. Their prefix sums are `[6,-2,-7,-4,-12,-24,-29,-9]`. With `L=2` and an input period of one cycle, products are offered on edges 1 through 8 and accumulated on edges 3 through 10. The final code is `-9`, or `-0.5625` at the product LSB of `1/16`.

The data view shows the same product sequence shifted by two edges. The control view shows valid shifted by exactly the same amount. The accumulator view holds zero while the pipeline fills, follows the prefix sums, and then holds the final value.

## Lever 1: product pipeline stages

Hold the input period at one cycle and sweep `L` from zero through four. First accumulation edges become `[1,2,3,4,5]`; completion edges become `[8,9,10,11,12]`. The modeled product-storage slots and valid bits each become `[0,1,2,3,4]`.

Mechanism first: each product register moves data, valid, and token identity one edge later. It does not edit a product code or reorder tokens. The eight accumulation events remain one edge apart and the final code remains `-9` at every depth. This schedule model does not calculate combinational delay or prove that a particular stage count improves clock rate.

## Lever 2: input period

Reset `L` to two and sweep the input period from one through four cycles per product. The healthy accumulation edges are the offered edges plus two. Completion edges become `[10,17,24,31]`, while the first accumulation stays at edge 3 because token 1 is always offered at edge 1.

Mechanism first: a larger input period inserts invalid bubble slots between products. Because the valid path and data path share the same delay, those bubbles emerge at the accumulator without losing or duplicating tokens. Accumulation-event spacing changes, elapsed completion time grows, and the final code still remains `-9`.

Bubble data is deliberately the legal nonzero product code `-56`, not zero. Valid is false, so that value has no numerical meaning and must be ignored. The nonzero diagnostic value makes an accidental update during a bubble visible.

## Deliberately broken case

Return to `L=2` and a one-cycle input period, but let valid and token identity bypass the two product registers. Product data still experiences the declared delay. The first two broken valid pulses therefore accumulate empty zeros. The next six valid-token labels name older product data, and product tokens 7 and 8 reach the accumulator after broken valid has ended.

The broken path performs eight apparent accumulation events but consumes only six real products. Its final code freezes at `-24`, or `-1.5`, instead of the healthy `-9`, or `-0.5625`. The exact violated assumption is equal delay for product, valid, and token identity. The recognizable symptom is a plausible-looking valid cadence paired with stale data and a running sum that stops before the pipeline tail drains.

At `L=0`, the fault is inert because there is no product delay to bypass. That limiting case confirms that misalignment—not a different multiplication rule—causes the error.

## Common mistakes

- Counting `L` as total MAC latency including an extra adder stage; this lesson defines `L` only as product delay and observes the accumulator update on the arrival edge.
- Treating a bubble as a zero-valued valid product. A bubble has `valid=0` and must not update state; a valid zero product would update by zero but still consume a token.
- Delaying data without its valid bit or assuming token order alone will repair the association.
- Assuming more stages automatically prove a faster clock, timing closure, or greater throughput.
- Treating product-delay stages as proof that the accumulator feedback path was retimed or interleaved.
- Forgetting that multiplying two operands with two fractional bits produces four fractional bits.
- Calling modeled storage slots or accumulator word length synthesis evidence or synthesized FPGA resources.
- Inferring HDL, reset, backpressure, multiplier sharing, converter, or physical behavior from the deterministic cycle model.

## Completion standard

Run `run_checks.m`, answer `checks.md` one prompt at a time, identify the two dropped tokens from the broken symptom, and give the requested two-sentence teach-back without explaining MATLAB syntax.
