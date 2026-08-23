# Lesson: Build Combinational Logic from Truth Tables

## Guiding question

What inputs, observable effects, and failure modes matter when you build Combinational Logic from Truth Tables?

## Mental model

Treat `ABC` as a three-bit address, with `A` most significant and `C` least significant. Address `4A+2B+C` selects one of eight rows, and that row supplies `Y`. A complete combinational specification covers every reachable input and depends only on current inputs.

## Connection to P01

P01 made stored FIFO occupancy and earlier traffic visible. P02 instead makes a current-word decision with no stored history: it has no remembered occupancy or previous input. A real datapath can place this truth-table logic before or after the P01 queue; P03 will add state deliberately with registers.

## Learning cycle

Read the address model, visualize the baseline, move one lever, inspect the changed view, and then read the mechanism-first explanation. Reset before moving the second lever so mapping changes and row-frequency changes remain distinct.

## One prediction before the baseline

For the 2-of-3 voter, predict `Y` for `ABC=011`. Then inspect the exhaustive baseline once. The expected vector from address `000` to `111` is `[0 0 0 1 0 1 1 1]`, because at least two inputs are HIGH in exactly four rows.

## Lever 1: required-HIGH threshold

Hold `p=0.5` and change only `k`:

- `k=1`: `Y=A OR B OR C`; seven rows assert.
- `k=2`: `Y=(A AND B) OR (A AND C) OR (B AND C)`; four rows assert.
- `k=3`: `Y=A AND B AND C`; one row asserts.

Mechanism first: changing `k` changes the Boolean specification, so the truth-table mapping changes.

## Lever 2: input-HIGH probability

Reset to `k=2` and change only `p`. Under the explicit assumption that A, B, and C are independent and each is HIGH with probability `p`, a row with `h` HIGH bits has weight

\[
p^h(1-p)^{3-h}.
\]

The eight output bits remain fixed, but their occurrence weights change. For majority logic,

\[
P(Y=1)=3p^2(1-p)+p^3=3p^2-2p^3.
\]

Mechanism first: `p` changes expected traffic through the rows, not the combinational function.

## Deliberately broken case

Enable the fault that flips LUT address `6` (`ABC=110`). Seven rows still match, so spot-checking `000`, `011`, or `111` can miss the defect. Exhaustive comparison reports exactly one mismatch. The violated assumption is specific: every reachable LUT entry matches its specified truth-table row.

This is a deterministic configuration/specification mismatch, not a claim that a physical radiation event or timing hazard was simulated.

## Common mistakes

- Confusing zero-based LUT address `6` with MATLAB row index `6`; the MATLAB row is `address+1`.
- Reversing A and C and silently changing bit significance.
- Calling four asserted rows “50% runtime HIGH” without first assuming uniform input rows.
- Testing only favorite examples instead of all eight combinations.
- Saying combinational logic is instantaneous; the abstraction has no stored state, while real gates still have propagation delay.
- Inferring glitch, timing, or FPGA resource behavior from this static truth table.

## Completion standard

Run `run_checks.m`, answer the interpretation prompts in `checks.md` one at a time, diagnose address `6`, and give the requested two-sentence teach-back without explaining MATLAB syntax.
