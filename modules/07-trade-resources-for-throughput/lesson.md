# Lesson: Trade Resources for Throughput

## Guiding question

What inputs, observable effects, and failure modes matter when you trade Resources for Throughput?

## Mental model

Imagine each multiplier pipeline as a checkout lane. A frame brings eight independent products. One lane reuses the same multiplier eight times; eight lanes accept the whole frame together. Intermediate lane counts pack products into groups, and the final group may be only partly full.

P06 established the numerical and timing identity of one product: signed `W=4`, `I=1` excluding sign, `F=2` operands produce an eight-bit product code with four fractional bits, and the modeled product pipeline adds two cycles while accepting a new product every cycle. P07 preserves those facts. It changes only how many identical product lanes exist and when frames may claim them.

For `W=8` products and `R` lanes, healthy issue time is

\[
G=\left\lceil\frac{8}{R}\right\rceil\quad\text{cycles/frame}.
\]

Ceiling matters because a partial final group still consumes a cycle. A finite source offers frames every `A` cycles, and the non-preemptive scheduler starts frame `j` only after it arrives and the prior frame releases the lanes:

\[
s_j=\max\left(a_j,s_{j-1}+G\right).
\]

The product lane's two-cycle latency shifts result visibility but does not change its one-operation-per-cycle acceptance rate. Keep four quantities distinct:

- lane latency: two cycles from issue edge to result edge;
- lane initiation interval: one cycle per product;
- non-preemptive frame capacity interval: `G` cycles per frame;
- scheduled output interval: `max(A,G)` cycles per frame.

The `R` lanes expose `R` raw product-issue slots per cycle, equivalent to `R/8` frames of work per cycle. This lesson's frame-at-a-time policy deliberately leaves the unused lane in a partial final group idle. Its complete-frame capacity is therefore the raw frame-equivalent rate multiplied by packing utilization `8/(R G)`, which gives `1/G`.

## Connection to P06

P06 delayed one ordered MAC product stream and showed why product, valid, and identity travel together. P07 assigns each product a frame identity, operation identity, and lane identity. Its output is an eight-product vector with a valid bit for every position. The same equal-identity discipline lets the checks prove that replication neither duplicates nor drops work.

The six input vectors are deterministic circular shifts of P06's input codes; coefficients and the `1/16` product LSB remain fixed. Diagnostic checksum codes `[-9,72,23,-16,69,-6]` make a missing tail visible, but there is no modeled checksum adder. Treat the vector and valid mask—not the checksum—as the datapath result.

## Learning cycle

Read the resource-capacity contract, visualize the baseline, move one lever, inspect the changed view, and then read the mechanism-first explanation. Reset before moving the second lever so lane replication and source demand remain independent.

## One prediction before the baseline

The baseline has eight products, two lanes, and a two-cycle lane latency. Predict how many issue cycles one frame reserves and how many edge differences separate its arrival at edge 1 from its final product result. Then inspect the baseline once. Make no second prediction; later prompts ask you to observe and explain.

## Baseline

With `R=2`, healthy ceiling division gives `G=4`. Frames arrive every `A=4` cycles, exactly matching capacity, so arrivals and starts are `[1,5,9,13,17,21]`, wait is zero, and completion edges are `[6,10,14,18,22,26]`. The first frame issues product pairs on edges 1 through 4; the last pair appears after the two-cycle lane delay on edge 6.

Both lanes are occupied in all four issue groups, so packing utilization is 100 percent. Non-preemptive frame capacity and scheduled throughput are both `1/4` frame/cycle. At the explicit 100 MHz teaching assumption this is 25 Mframes/s; no actual clock performance is claimed.

## Lever 1: modeled multiplier lanes

Hold the source interval at one cycle and sweep `R=1..8`. Capacity intervals become `[8,4,3,2,2,2,2,1]` cycles/frame. The first frame's edge latency becomes `[9,5,4,3,3,3,3,2]` cycles, and maximum wait across the six-frame finite queue becomes `[35,15,10,5,5,5,5,0]` cycles.

Mechanism first: each added lane creates another operation slot in each issue group. The ceiling only falls when the new total covers eight products in fewer groups. Four, five, six, and seven lanes all need two groups; their idle final-group slots are `[0,2,4,6]`. More modeled resources can therefore leave throughput unchanged when integer packing is the limit. Eight lanes reach one frame per cycle under the ideal lane assumptions.

## Lever 2: offered frame interval

Reset to `R=2`, so capacity remains four cycles/frame, then sweep `A=1..8`. Scheduled intervals become `[4,4,4,4,5,6,7,8]`. Maximum waits become `[15,10,5,0,0,0,0,0]` cycles.

Mechanism first: when `A<G`, frames arrive faster than the two lanes can serve them, so this finite ideal queue stores the difference and wait grows. When `A=G`, demand and capacity balance. When `A>G`, lanes finish before the next frame arrives; the source, not compute capacity, limits scheduled throughput. Changing demand does not change lane count, product codes, or the capacity equation.

This module deliberately stops at the finite-queue observation. Later modules introduce valid/ready, backpressure, and FIFO sizing; do not infer that an indefinitely overloaded source can be accepted without bounded storage or flow control.

## Deliberately broken case

Set `R=3` and `A=2`, then replace ceiling with floor division:

\[
G_{broken}=\left\lfloor\frac{8}{3}\right\rfloor=2.
\]

Two groups of three lanes create only six slots. The controller starts a new frame every two cycles, drops operations 7 and 8 from every frame, and falsely claims 0.5 frame/cycle (50 Mframes/s at the teaching clock). The correct non-preemptive capacity interval is three cycles and the correct demand-limited complete-frame rate is `1/3` frame/cycle.

Every output vector is incomplete. Frame 3's diagnostic checksum is code 13 instead of 23; across all frames the incomplete checksum codes are `[-24,47,13,-1,39,-21]`. The violated assumption is `R*G >= W`: floor division breaks it whenever `R` does not divide eight. The fault is inert for exact divisors `R=1,2,4,8`, which confirms that missing coverage—not arithmetic or pipeline latency—causes the symptom.

## Common mistakes

- Using floor division for resource groups and forgetting the partial final cycle.
- Calling lane latency the frame initiation interval; a two-cycle lane can still accept one new product every cycle.
- Assuming more lanes always improve throughput despite integer packing or insufficient source demand.
- Treating 100 MHz as achieved timing rather than an explicit unit-conversion assumption.
- Calling a modeled multiplier lane a DSP slice, or treating modeled storage bits as a utilization report.
- Counting only numerical values and ignoring each product's valid, frame identity, and operation identity.
- Calling the diagnostic checksum a modeled reduction datapath.
- Assuming the finite ideal queue proves lossless sustained overload, backpressure, or FIFO sufficiency.

## Completion standard

Run `run_checks.m`, answer `checks.md` one prompt at a time, identify the exact missing operations in the broken case, distinguish latency from initiation interval, and give the requested two-sentence teach-back without explaining MATLAB syntax.
