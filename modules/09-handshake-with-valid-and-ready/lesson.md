# Lesson: Handshake with Valid and Ready

## Guiding question

What inputs, observable effects, and failure modes matter when you handshake with Valid and Ready?

## Mental model

Treat `valid` and `ready` as two independent promises sampled at a rising edge. The producer owns `valid` and `data` and promises that its payload is meaningful by asserting `valid`; the consumer owns `ready` and promises capacity by asserting it. A token crosses only on an edge where both promises are true:

\[
\text{transfer}[n]=\text{valid}[n]\land\text{ready}[n].
\]

In compact signal notation, `transfer[n] = valid[n] && ready[n]`.

If the producer is valid and the consumer is not ready, nothing transferred. The producer therefore still owes the same token on the next cycle: `valid` stays high and `data` stays unchanged. The consumer may assert `ready` before or after `valid`; ready alone never invents a transfer.

## Connection to P08

P08 generated visible 12-bit phase codes. P09 reuses the first eight codes from `K=411` as unmistakable payload labels, then asks when each code crosses a block boundary. The list is precomputed for this finite lesson. A real free-running NCO does not automatically pause with this source; preserving continuously generated samples needs buffering or an explicit source-control contract, which belongs beyond this single-link handshake.

## Learning cycle

Read the signal-ownership rule, visualize the baseline, move one lever, inspect the changed view, and then read the mechanism-first explanation. Reset before moving the second lever so producer spacing and consumer availability remain independent.

## One prediction before the baseline

In the baseline, token 822 is valid at cycle 5 while ready is low. Predict whether it transfers at cycle 5 or remains owed. Then inspect the baseline once. Make no second prediction; later prompts ask you to observe and explain.

## Baseline

With one source gap and a three-cycle consumer stall, the eight transfer edges are `[1, 3, 8, 10, 12, 14, 16, 18]`. At cycles 5, 6, and 7, `valid=1`, `ready=0`, and `transfer=0`; token 822 remains stable. At cycle 8, ready returns and exactly that token transfers. The active window contains eight transfers, three stalled-valid cycles, and seven source bubbles.

The four combinations have distinct meanings:

- `valid=0, ready=0`: no offer and no capacity; no transfer.
- `valid=0, ready=1`: capacity without an offer; no transfer.
- `valid=1, ready=0`: an owed token is stalled and must be held.
- `valid=1, ready=1`: exactly one transfer occurs at the edge.

## Lever 1: source gap

Hold the consumer always ready and sweep `sourceGapCycles=0..3`. Completion moves from cycle 8 to cycles 15, 22, and 29. The number of source bubbles before completion is `7*sourceGapCycles`, because gaps occur only between the eight tokens. Payload codes, order, ready, and transfer correctness stay fixed.

Mechanism first: a bubble is a cycle with no valid offer. Ready cannot accept a token that was not offered. With zero gaps, one token transfers on every cycle; inserting gaps reduces the modeled completion-window rate without changing any payload.

## Lever 2: ready stall

Reset to a continuously valid source and sweep `readyStallCycles=0..6` from fixed start cycle 5. Completion moves from cycle 8 through cycle 14. Maximum token wait and stalled-valid count each equal the ready-low duration; all eight payloads still arrive once and in order.

Mechanism first: while ready is low, the pending token consumes no transfer. The producer holds it, so each extra low-ready cycle delays that token and every later token by one cycle. Ready returning creates a transfer only because valid and the held data are still present.

## Deliberately broken case

Use zero source gaps and a three-cycle ready stall, but incorrectly advance the producer after every valid offer even when ready is low. Tokens 1644, 2055, and 2466 are discarded on cycles 5, 6, and 7. The consumer receives `[0, 411, 822, 1233, 2877]`; three payloads are missing even though the remaining order looks plausible.

The violated rule is “advance producer state only on `valid && ready`.” Data also changes after each stalled cycle, creating hold-rule violations on cycles 6, 7, and 8. With no stalled-valid cycle the fault is inert, which isolates missing ready qualification as the cause rather than arithmetic corruption.

## Common mistakes

- Treating `valid` as a one-cycle request pulse that may disappear when ready is low.
- Counting `valid` or `ready` alone as a transfer.
- Changing data while valid remains high through a stall.
- Advancing counters, pointers, or state machines on `valid` instead of `valid && ready`.
- Assuming ready must wait for valid; independent early ready is legal in this model.
- Calling modeled transfer rate measured throughput or achieved interface throughput, or treating payload width as measured FPGA utilization.
- Assuming this single-clock model proves clock-domain crossing (CDC) safety, combinational-loop freedom, FIFO sizing, packet integrity, synthesis, achieved timing, or deadlock freedom.

## Completion standard

Run `run_checks.m`, answer `checks.md` one prompt at a time, identify all four valid/ready cases, explain both isolated sweeps, diagnose the exact three-token loss, distinguish the precomputed P08 payload labels from a pausable NCO, and give the requested two-sentence teach-back without explaining MATLAB syntax.
