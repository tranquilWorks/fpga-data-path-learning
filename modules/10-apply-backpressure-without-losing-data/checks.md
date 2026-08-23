# P10 checks: Apply Backpressure Without Losing Data

## Guiding question

What inputs, observable effects, and failure modes matter when you apply Backpressure Without Losing Data?

Run `run_checks` first. It independently checks the exact baseline, both handshake equations, occupancy conservation, stable holds, two isolated sweeps, limiting cases, the deliberately broken case, all bounded control combinations, malformed input rejection, deterministic recovery, and fixed teaching-model resource bounds.

Then answer one prompt at a time.

## Observation and mechanism checks

1. On which baseline cycles is consumer ready low, and on which cycles does backpressure actually pause the source? Explain the difference using the two free FIFO slots.
2. Name the upstream enqueue and downstream dequeue equations. Why is `valid=1` alone insufficient on either interface?
3. Use `qAfter=qBefore+enqueue-dequeue` to explain one fill edge, one no-motion full edge, one simultaneous full replacement edge, and one drain-only edge.
4. Why can a full FIFO assert source ready on a cycle with a downstream dequeue?
5. Which source token and FIFO-output token are held, and what observation proves each hold is stable?

## Independent sweep checks

6. In the stall-duration sweep, explain completion `13+stallCycles`, peak occupancy `min(3,1+stallCycles)`, and source stalls `max(0,stallCycles-2)` without reading MATLAB syntax.
7. In the depth sweep, why do source stalls fall from five to zero while completion remains cycle 18 and delivery remains 12 tokens?
8. State what is held fixed in each sweep. If both levers moved together, which causal conclusion would become ambiguous?

## Combined-control boundary check

9. At depth four, why do three consumer ready-low cycles fill the three free slots without pausing the source, while a fourth ready-low cycle pauses token 8 exactly once? Explain why the broken switch is inert in the first case but drops exactly token 8 in the second.

## Limiting-case checks

10. Depth one with no consumer stall is the registered replacement limit: enqueue cycles 1–12, dequeue cycles 2–13, peak occupancy one, and no source stall. Why is the minimum residence one cycle?
11. Depth one with the longest stall pauses the source on cycles 5–12 but loses nothing. Depth six with the five-cycle stall never pauses the source. Explain both with capacity, not consumer speed.
12. The maximum healthy controls still complete by cycle 21 inside the 24-cycle record. What does that finite bound prove, and what does it not prove about a never-ready consumer or timeout policy?

## Broken-case and recovery checks

13. The broken producer drops token indices 7–9/codes `[2466,2877,3288]` on cycles 7–9 and violates the source hold rule on cycles 8–10. Why are the violation cycles shifted by one?
14. The broken consumer-visible sequence is `[1:6,10:12]`, while FIFO occupancy never exceeds three. Locate the loss boundary precisely: which component broke which P09 obligation?
15. Why is the broken switch inert in the no-stall and depth-six/five-stall limits? Distinguish selecting a fault from activating its precondition.
16. After malformed calls and unrelated maximum/fault calls, why must the exact baseline return? Relate that recovery check to absence of global, persistent, file, network, timer, or asynchronous state.

## Interpretation and transfer check

Connect P09's stable valid/ready offer to P10's FIFO propagation without claiming that a free-running source can always pause. Distinguish this finite, single-clock conservation model from P11 packet framing, P12 burst/rate FIFO sizing, CDC safety, combinational-ready timing closure, synthesis, measured throughput, and deadlock/liveness evidence.

## Teach-back

In two sentences, answer the guiding question. Sentence one must explain how the two handshakes and occupancy recurrence apply backpressure while conserving ordered tokens. Sentence two must name the exact ignored-ready failure symptom and why finite storage cannot recover the discarded offers.
