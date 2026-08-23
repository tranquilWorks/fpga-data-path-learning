# P10 — Apply Backpressure Without Losing Data

**Track:** FPGA, Converter Interfaces, and High-Speed Data Paths  
**Phase 3:** Streaming architectures  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you apply Backpressure Without Losing Data?

## Computational mental model

P09 established one valid/ready link: a token transfers only when both sides agree on one edge, and a stalled sender holds the token still owed. P10 places a finite, registered FIFO between two such links:

```text
producer valid/data  ->  FIFO  ->  consumer valid/data
             ready  <-        <-  ready
```

Immediately before edge `n`, `q[n]` is the number of stored tokens and `D` is the selected FIFO depth. The output may remove one token, and that removal may create the slot used by one simultaneous input transfer:

\[
\begin{aligned}
\text{dequeue}[n] &= \text{outputValid}[n]\land\text{consumerReady}[n],\\
\text{sourceReady}[n] &= (q[n] < D)\lor\text{dequeue}[n],\\
\text{enqueue}[n] &= \text{sourceValid}[n]\land\text{sourceReady}[n],\\
q[n+1] &= q[n]+\text{enqueue}[n]-\text{dequeue}[n].
\end{aligned}
\]

The FIFO is not fall-through: a token enqueued on one edge can first be dequeued on the next edge. When the consumer stalls, stored occupancy rises. Once no slot can be promised, `sourceReady` falls and the producer must hold its current valid payload. Backpressure changes when tokens move; it must not change which tokens eventually arrive.

## Deterministic baseline

The baseline uses FIFO depth 3, consumer ready low on cycles 5–9, 12 payload labels derived from P09's 12-bit phase codes, and a fixed 24-cycle record.

- Enqueue edges: `[1:6, 10:15]`.
- Dequeue edges: `[2:4, 10:18]`.
- Source backpressure edges: cycles `7:9`.
- Peak occupancy: 3 tokens.
- Maximum source offer-to-enqueue wait: 3 cycles.
- Maximum FIFO residence: 6 cycles.
- Completion: cycle 18 with all 12 payloads delivered exactly once and in order.

The consumer's five-cycle pause is partly absorbed by the two free slots present after cycle 4. The remaining three cycles propagate upstream as `sourceReady=0`. Output token 4 stays stable through the consumer stall, while source token 7 stays stable through the propagated backpressure.

## Two independent levers

1. **Consumer ready-low duration, 0–8 cycles:** FIFO depth stays 3. Completion moves from cycles 13 to 21; peak occupancy grows to 3; only stall time beyond the two free slots reaches the producer. Delivery remains 12 ordered tokens.
2. **FIFO depth, 1–6 tokens:** consumer ready stays low for five cycles. Each added slot removes one source-stalled cycle, while completion remains cycle 18 because storage cannot replace missing consumer service. This bounded comparison makes propagation visible; it is not a FIFO-sizing proof from arrival and service rates, which belongs to P12.

## Deliberately broken case

The broken producer advances its payload every valid cycle even when `sourceReady=0`. In the baseline, the full FIFO rejects token indices 7–9 on cycles 7–9. The source changes its supposedly held payload on cycles 8–10, and the consumer later sees `[1:6, 10:12]`. The FIFO remains within three slots; loss occurs because the producer discarded offers that no handshake accepted.

The fault is inert when the healthy schedule never lowers ready for a valid source offer, such as a no-stall run or the depth-six/five-stall case.

## Learning flow

1. Read the two handshake equations and make one prediction about when backpressure reaches the producer.
2. Run `lesson.m` or reveal `experiment.m` one `%%` section at a time.
3. Observe upstream handshakes, downstream handshakes, occupancy, and held token identity.
4. Move the consumer-stall lever, read the changed-view mechanism, then reset it.
5. Move the FIFO-depth lever and explain why completion does not improve.
6. Enable the broken producer and identify the exact missing tokens.
7. Run `interactive`, `run_checks`, answer `checks.md` one prompt at a time, and give the two-sentence teach-back.

## Files

- `model.m` — presentation-free, deterministic FIFO state and accounting.
- `experiment.m` — baseline, two isolated sweeps, labeled metrics, and broken case.
- `interactive.m` — bounded depth, stall, observation-cycle, and fault controls.
- `lesson.m`, `lesson.md`, and `walkthrough.md` — learner and tutor sequence.
- `run_checks.m` and `checks.md` — numerical, limiting-case, interpretation, and teach-back checks.

## Evidence boundary

This repository retains a deterministic source model and independently specified static tests. It does not claim that MATLAB executed here, figures rendered, UI callbacks ran, or numerical behavior was validated by a MATLAB runtime. The model assumes one clean clock and finite consumer recovery. It omits reset, clock-domain crossing, metastability, combinational ready loops and timing closure, packet boundaries, arbitration, burst/rate-derived FIFO sizing, an unpausable source, timeout policy, starvation, fairness, system deadlock, HDL, synthesis, placement, routing, and measured throughput. The 24-cycle record, 12 payload labels, six-slot maximum, and 12-bit codes are teaching-model bounds, not measured or synthesized FPGA resources. Bench, HIL, field, deployment, and production behavior require separate retained evidence.
