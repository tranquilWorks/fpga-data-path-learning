# Checks: Handshake with Valid and Ready

What inputs, observable effects, and failure modes matter when you handshake with Valid and Ready?

Ask and answer one prompt at a time.

## Observation check

For the one-gap, three-stall baseline, name the owners of `valid`, `data`, and `ready`; the pre-edge sampling convention; all four valid/ready combinations; the eight transfer cycles; the token held from cycles 5 through 8; and the active-window transfer, stall, and source-bubble counts. Which quantities are deterministic teaching values rather than measured hardware facts?

## Lever-isolation check

With ready always high, what changes as source gap moves from zero through three, and why are there `7*g` bubbles? After resetting source gap to zero, what changes as ready-low duration moves from zero through six? Name the ready schedule, payload values, accepted order, and counts that each sweep must preserve.

## Limiting-case check

Explain the always-valid/always-ready one-transfer-per-cycle limit, early ready with no valid offer, ready low entirely inside a source bubble, a ready-low interval that overlaps only the next valid offer, valid held through the longest ready stall, the maximum combined case that completes exactly on cycle 35, and a ready return after a stalled token. Why does neither input alone imply a transfer, and why may payload change immediately after an accepting edge?

## Broken-case check

With zero source gaps and ready low on cycles 5 through 7, why does advancing on valid alone drop payloads 1644, 2055, and 2466? Identify the five accepted payloads, three drop edges, three next-cycle hold violations, and the no-stall limit where the fault becomes inert.

## Interpretation and transfer check

Connect P08's numeric phase code to P09's token identity without claiming that a free-running NCO pauses. Distinguish this single-link transfer rule from P10-style backpressure propagation, FIFO sizing, CDC safety, packet framing, achieved clock rate, synthesized resources, and measured throughput.

## Executable check

Run in MATLAB:

```matlab
run_checks
```

All assertions must pass before completion. They cover the exact baseline, all four handshake cases, both isolated sweeps, always-ready and maximum-bound limits, the exact broken loss/hold symptom, inert-fault recovery, every bounded healthy/fault control pair, malformed inputs, accepted numeric-class equivalence, deterministic recovery, and fixed trace/token bounds.

## Teach-back

In two sentences, answer: “What inputs, observable effects, and failure modes matter when you handshake with Valid and Ready?” Sentence one must explain ownership, the `valid && ready` transfer edge, and the stable-data obligation during a stall. Sentence two must connect advancing without ready to missing tokens and name completion cycle, wait, or transfer rate as an observable symptom without relying on MATLAB syntax.
