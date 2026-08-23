# Checks: Store State with Registers

Ask and answer one prompt at a time.

## Observation check

At baseline edges 1, 3, and 6, identify `D` before the edge, `Q` after it, reset, enable, and validity. Why is the zero at edge 1 not an accepted zero-valued token?

## Lever-isolation check

What changes when depth moves from 1 to 3, and what input and enable facts stay fixed? After resetting to one stage, what changes when enable period moves from 1 to 3, and what stage, clock, and input facts stay fixed?

## Limiting-case check

Explain why one stage has no additional enabled-edge delay relative to `Q1`, why four stages first become valid at cycle 5, why period 1 has no post-reset holds, and why the broken cascade is inert at depth 1.

## Broken-case check

At cycle 4, why is healthy state `[5 13 2]` while broken state is `[5 5 5]`? Name the exact simultaneous-sampling assumption that the broken calculation violates and the early-output symptom it creates.

## Interpretation and transfer check

How could P02 combinational logic drive this register's `D`? Give one reason to use enable and one reason to use reset, then name a setup/hold or clocking fact this edge-level model assumes rather than proves.

## Executable check

Run in MATLAB:

```matlab
run_checks
```

All assertions must pass before completion. They cover the exact trace, reset priority, capture and hold recurrence, simultaneous stage transfer, depth and enable limits, malformed inputs, the broken cascade, invalid-state bookkeeping, fixed resource bounds, deterministic recovery, and call isolation.

## Teach-back

In two sentences, answer: “What inputs, observable effects, and failure modes matter when you store State with Registers?” Sentence one must explain reset, enable, capture, and hold using pre-edge input and post-edge state. Sentence two must explain how stage depth changes enabled-edge delay and how violating simultaneous pre-edge sampling creates an early, incorrect output.
