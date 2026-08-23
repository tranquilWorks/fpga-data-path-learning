# P12 checks: Size a FIFO from Burst and Service Rates

## Guiding question

What inputs, observable effects, and failure modes matter when you size a FIFO from Burst and Service Rates?

Run `run_checks` first. It independently checks the registered recurrence, exact baseline, finite
capacity accounting, two isolated sweeps, limits, broken estimator, complete bounded control grid,
malformed inputs, numeric-class compatibility, deterministic recovery, and fixed resource bounds.

Then answer one prompt at a time.

## Observation and mechanism checks

1. Which baseline edges offer three words, and why is the first actual departure on cycle 2 rather
   than cycle 1?
2. State the unbounded recurrence for `qAfter[n]`. Why must required depth be its maximum rather than
   the maximum of a finite FIFO trace?
3. Derive occupancy `[3,5,7,9,11,13,15,17]` from `B=8`, `A=3`, `S=1`, and empty initial state.
4. Why does exact depth 17 have zero minimum headroom yet admit and depart all 24 words?
5. Use offered = admitted + not accepted and admitted = departed + final occupancy to explain the two
   conservation checks.

## Independent sweep checks

6. In the burst-duration sweep, derive `[3,5,9,13,17]` words. Which arrival, service, depth, timing,
   and fault values stay fixed so the causal result is isolated?
7. In the service sweep, derive `[24,17,10,3,3]` words. Why does required depth stop falling once
   service reaches three words/cycle?
8. Why does zero service return `no drain` while positive-service grid cases complete by cycle 33?
   Distinguish a bounded traffic result from an execution timeout or liveness proof.
9. If burst duration and service rate moved together, why could their effects on required depth no
   longer be attributed independently?

## Registered limits and finite capacity

10. With matched `A=S=3`, trace the first two edges. How does the FIFO remain at three words while
    dequeue and admission replace three stored words on the same later edge?
11. Why does faster service still require the first three-word staging batch in this model? What
    architecture change could alter that conclusion?
12. With depth 16 in the baseline, why is exactly one cycle-eight word not accepted, and why does the
    admitted subset drain on cycle 24?
13. With depth zero, what can and cannot happen in a registered non-fall-through FIFO? Do not call a
    zero-depth direct path equivalent without a separate bypass contract.

## Deliberately broken case and recovery

14. The fall-through formula gives 16 while the registered formula gives 17. Name the exact same-edge
    assumption that creates the difference.
15. Why can the broken occupancy plot appear safely capped at 16? Which admission metric exposes the
    hidden shortfall?
16. A full FIFO does not automatically lose the unaccepted word. Explain how P10/P11 valid-ready hold
    and retry preserves it, and name the source condition under which it becomes conditional loss.
17. Why is the broken switch inert at zero service even though that case never drains?
18. After malformed calls, a maximum-bound call, a zero-service call, and the fault call, why must the
    exact baseline return? Relate this to the absence of global, persistent, file, network, timer, or
    asynchronous state.

## Interpretation and transfer check

Connect P01's qualitative burst intuition, P10's registered timing, and P11's framed valid/ready
offers to this exact sizing calculation. State which extra inputs are needed to convert modeled words
into bytes, packets, BRAM geometry, almost-full thresholds, timing margin, or a CDC-safe implementation.
Explain why the fixed 40-cycle model does not validate timeout/cancellation policy, MATLAB UI behavior,
synthesis, measured throughput, bench, HIL, field, or production operation.

## Teach-back

In two sentences, answer the guiding question. Sentence one must explain how maximum unbounded
registered backlog, burst duration, ingress rate, guaranteed service, initial occupancy, and margin
determine depth. Sentence two must name the exact 17-versus-16 failure symptom and distinguish required
backpressure from conditional loss when ready/hold is ignored.
