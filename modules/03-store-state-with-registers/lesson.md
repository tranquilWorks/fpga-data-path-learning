# Lesson: Store State with Registers

## Guiding question

What inputs, observable effects, and failure modes matter when you store State with Registers?

## Mental model

Draw a boundary at each rising clock edge. `D[n]` is the code immediately before edge `n`; `Q[n]` is stored state immediately after it. Synchronous reset wins first, enable chooses capture or shift second, and disable means hold. Between edges, `Q` remembers its value even while `D` changes.

For the first register:

\[
Q_1[n]=0\text{ on reset},\qquad Q_1[n]=D[n]\text{ when enabled},\qquad Q_1[n]=Q_1[n-1]\text{ when disabled}.
\]

Every enabled later stage samples the preceding stage's pre-edge state:

\[
Q_s[n]=Q_{s-1}[n-1],\quad s>1.
\]

## Connection to P02

P02's combinational truth table answered from current bits and had no stored history. Its result can feed `D`, but a register determines when that result is captured as `Q` and preserves it when enable is LOW. P03 therefore adds time and memory to P02's current-input decision without changing that Boolean decision itself.

## Learning cycle

Read the edge convention, visualize the baseline, move one lever, inspect the changed view, and then read the mechanism-first explanation. Reset before moving the second lever so added state depth and changed capture cadence remain distinct.

## One prediction before the baseline

For one stage with reset only on cycle 1 and enable HIGH afterward, predict `Q` immediately after edge 3 when `D=13`. Then inspect the baseline once. Make no second prediction: subsequent prompts ask you to observe and explain.

## Baseline

The fixed trace has 16 rising edges and 4-bit unsigned codes. At edge 1, reset loads `Q=0` even though `D=9` and enable is HIGH. That reset-fill code is marked invalid. From edge 2 onward, the one-stage register is enabled on every edge, so post-edge `Q` equals the pre-edge `D` for that same numbered edge.

Do not call the overlaid one-stage traces “zero hardware latency.” The input is observed before the edge and the output after it; the plot deliberately uses the same edge number for those two sides of the event.

## Lever 1: register depth

Hold enable period at 1 and sweep stage count from 1 through 4. The same accepted input order reaches the last stage, but each stage after `Q1` adds one enabled-edge delay and four modeled data-storage bits. First-valid cycles become `2`, `3`, `4`, and `5`.

Mechanism first: on one edge, every physical register observes its input from pre-edge state. `Q2` cannot use the value that `Q1` has only just captured, so that value advances at the next enabled edge.

## Lever 2: enable period

Reset to one stage and sweep enable period from 1 through 4 cycles. Period 1 captures 15 post-reset samples; period 4 captures 4 and holds on 11 non-reset edges. The clock still has 16 rising edges—the enable changes which edges modify state, not clock frequency.

Mechanism first: a disabled edge selects feedback from the existing `Q`, so the previous code remains observable while uncaptured `D` values pass by.

## Deliberately broken case

With three stages, enable the broken cascade. It computes `Q1` from the new `D`, then incorrectly gives that new `Q1` to `Q2` and the new `Q2` to `Q3` on the same edge. At edge 4, the healthy state is `[5 13 2]`; the broken state is `[5 5 5]`. The last-stage output becomes valid two edges too early and disagrees with the simultaneous-transfer reference on cycles 2 through 16.

The violated assumption is precise: all edge-triggered registers sample their inputs from pre-edge state simultaneously. This deterministic bad calculation is not a physical propagation, setup/hold, or metastability simulation.

## Common mistakes

- Comparing `D` and `Q` without saying which side of the edge each represents.
- Treating reset-fill bits as an accepted zero-valued token; inspect validity as well as bits.
- Saying every extra stage always adds one wall-clock cycle when enable can stall the pipeline; it adds one enabled-edge delay.
- Treating enable as a slower clock. The clock edges remain; disabled registers hold.
- Updating stages left-to-right from newly computed values and collapsing their intended history.
- Calling `dataStorageBitCount` measured FPGA utilization. It is only 4 data bits per modeled stage; validity is simulator bookkeeping.
- Inferring setup/hold margin, metastability, timing closure, or hardware behavior from this edge-level model.

## Completion standard

Run `run_checks.m`, answer `checks.md` one prompt at a time, diagnose the cascade symptom, and give the requested two-sentence teach-back without explaining MATLAB syntax.
