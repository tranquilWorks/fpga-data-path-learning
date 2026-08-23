# P10 lesson: Apply Backpressure Without Losing Data

## Guiding question

What inputs, observable effects, and failure modes matter when you apply Backpressure Without Losing Data?

## Compounds on P09

P09 assigned ownership: a producer owns `valid` and payload, a consumer owns `ready`, and a token transfers only on an edge with both high. P10 composes two of those links around a finite FIFO. The upstream producer sees readiness from the FIFO; the downstream consumer supplies readiness to the FIFO output. Each stalled sender must hold the valid payload still owed.

The 12 payload values are deterministic unsigned 12-bit phase-code labels extended from P09. They make identity and order visible; this lesson does not claim that a free-running NCO pauses or that these labels are continuously sampled converter data.

## The conservation mechanism

Observe signals immediately before edge `n`. Let `q[n]` be occupancy in tokens and `D` the selected depth:

\[
\begin{aligned}
\text{dequeue}[n] &= \text{outputValid}[n]\land\text{consumerReady}[n],\\
\text{sourceReady}[n] &= (q[n] < D)\lor\text{dequeue}[n],\\
\text{enqueue}[n] &= \text{sourceValid}[n]\land\text{sourceReady}[n],\\
q[n+1] &= q[n]+\text{enqueue}[n]-\text{dequeue}[n].
\end{aligned}
\]

In plain signal notation these are `enqueue[n]`, `dequeue[n]`, and the
`q[n+1]` occupancy recurrence; the equations describe transfers, not MATLAB
assignment order.

The `dequeue` term in `sourceReady` matters when the FIFO is full: one outgoing token creates a slot for one incoming token on the same edge. The FIFO is registered, not fall-through, so a token first appears at its output one cycle after enqueue.

## Learning cycle

### Read and make one prediction

Use the depth-three, five-cycle consumer-stall baseline. Predict only this: when the consumer lowers ready on cycle 5, does the producer stop immediately, or do the FIFO's free slots absorb some arrivals first?

### Visualize the baseline

Run the first baseline section, then reveal one view at a time:

1. Upstream `sourceValid`, propagated `sourceReady`, and `enqueue`.
2. Downstream `outputValid`, `consumerReady`, and `dequeue`.
3. FIFO occupancy and its three-token bound.
4. Source, FIFO-output, and delivered token identity.

Make no second prediction. Report the observed transitions first. The consumer stalls on cycles 5–9; the FIFO fills; the producer is paused only on cycles 7–9. All 12 tokens leave in order by cycle 18. Output token 4/code 1233 is held from cycles 5–10, and source token 7/code 2466 is held from cycles 7–10.

### Lever 1 and changed view

Sweep consumer ready-low duration from 0 to 8 cycles while depth remains 3. Completion becomes cycles 13–21. Peak occupancy is `min(3, 1+stallCycles)`. Source-stalled cycles are `max(0, stallCycles-2)` because two unused slots absorb the first two blocked downstream edges. Delivery count stays 12.

Mechanism first: the FIFO does not erase downstream delay. It retains accepted tokens and tells the producer when no more can be accepted safely.

### Lever 2 and changed view

Reset the stall to five cycles and sweep depth from 1 to 6 tokens. Source-stalled cycles become `[5,4,3,2,1,0]`; peak occupancy reaches the selected depth; completion stays cycle 18; all 12 tokens still arrive.

Mechanism first: capacity postpones backpressure but cannot create consumer service. This small sweep illustrates cause and effect. P12 will derive depth from burst and service rates; P10 does not claim that depths 1–6 are sufficient for another traffic pattern.

### Deliberately broken case

Enable “advance source while ready is low” at the baseline. The FIFO is full on cycles 7–9 and promises no acceptance. The broken producer advances anyway, dropping token indices 7–9 with codes `[2466,2877,3288]`. Its next-cycle hold violations appear on cycles 8–10. The consumer receives `[1:6,10:12]`; storage itself never exceeds three tokens.

The fault is behaviorally inert if the healthy schedule never backpressures a valid source offer. A selected switch is not evidence of an activated failure; inspect the drop events.

## Tutor prompts

Ask one prompt at a time:

1. Which edge first lacks downstream service, and which edge first lacks upstream acceptance?
2. Why can a full FIFO assert source ready when a dequeue occurs on the same edge?
3. Which term in the occupancy equation explains the flat full-occupancy plateau?
4. Why does greater depth reduce source stalls without moving the final dequeue edge?
5. In the broken case, where were token indices 7–9 last visible, and why can the FIFO not recover them?

## Correct these misconceptions directly

- “`valid=1` means the token entered the FIFO.” No: input transfer also requires `sourceReady=1` on that edge.
- “`ready=0` means a token was dropped.” No: a healthy source holds it. Loss requires violating that hold/advance contract or lacking another retention mechanism.
- “A full FIFO must always lower ready.” Not when a same-edge dequeue creates the replacement slot.
- “More depth makes the consumer faster.” No: depth changes buffering and upstream pause, not downstream readiness.
- “A bounded trace proves liveness.” No: this schedule always returns ready. A never-ready consumer, timeout, fairness, and system deadlock are outside the finite safety model.
- “This proves FIFO sizing, packet integrity, CDC safety, synthesis, or timing.” It proves none of those. P11 adds packet framing, and P12 addresses rate-based depth selection.

## Completion

Run `run_checks`, answer `checks.md` one prompt at a time, and give a two-sentence teach-back: one sentence for the two handshake/occupancy mechanism, and one for the ignored-backpressure failure symptom. Do not explain MATLAB syntax.
