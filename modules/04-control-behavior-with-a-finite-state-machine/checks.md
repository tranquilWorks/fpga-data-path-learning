# Checks: Control Behavior with a Finite-State Machine

Ask and answer one prompt at a time.

## Observation check

At baseline cycles 2, 5, 6, and 7, identify sampled inputs, state before the edge, state after it, and each Moore output. Why does the deadline at cycle 7 not create a timeout?

## Lever-isolation check

What changes when completion delay moves from one to six while timeout remains eight? After resetting completion delay to four, what changes when timeout moves from one to eight, and what completion facts stay fixed?

## Limiting-case check

Explain why delay one finishes at cycle 3, why timeout one ends `WAIT` after one busy cycle, why delay equal to timeout succeeds under the declared policy, and why reversing priority is inert when the two input pulses occur on different edges.

## Broken-case check

At cycle 6 of the equal-delay case, why is healthy state `DONE` while broken state is `TIMEOUT`? Name the exact transition-priority assumption and the recognizable wrong-output symptom.

## Interpretation and transfer check

Explain how P03's state register and a P02-style combinational decision form this FSM. Name one real design input that might replace `workDone`, then name an asynchronous-input, setup/hold, timer, or synthesis fact this edge-level model assumes rather than proves.

## Executable check

Run in MATLAB:

```matlab
run_checks
```

All assertions must pass before completion. They cover the exact trace, pre-edge/post-edge convention, Moore decode, two independent sweeps, all 64 healthy timing pairs, all eight exposed equal-delay fault cases, inclusive timeout boundary, late-event isolation, terminal recovery, malformed inputs, broken priority, fixed resource bounds, deterministic recovery, and call isolation.

## Teach-back

In two sentences, answer: “What inputs, observable effects, and failure modes matter when you control Behavior with a Finite-State Machine?” Sentence one must explain how current registered state and sampled inputs select next state and Moore outputs. Sentence two must explain how response/deadline timing and an incorrect tie priority change the observable terminal result.
