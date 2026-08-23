# P11 — Frame Packets Across a Stream

**Track:** FPGA, Converter Interfaces, and High-Speed Data Paths  
**Phase 3:** Streaming architectures  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you frame Packets Across a Stream?

## Computational mental model

P10 established that a producer holds a valid payload while `ready=0`. P11 adds a one-bit
end-of-packet sideband named `last`. Payload and `last` are one offered beat:

```text
producer: valid + payload + last  ->  consumer
                              ready  <-
```

Immediately before edge `n`, a beat is accepted only when both handshake signals are high:

\[
\text{transfer}[n] = \text{valid}[n]\land\text{ready}[n].
\]

An accepted beat with `last=1` closes the receiver's current packet. If `valid=1` and `ready=0`,
the source must hold payload and `last` together until an accepting edge. Seeing `last=1` on an
unaccepted cycle does not close a packet.

## Deterministic baseline

The baseline divides the 12 deterministic P10 payload codes into three four-beat packets. Consumer
`ready` is low on cycles 4–6 of a fixed 24-cycle teaching trace.

- Transfer edges: `[1, 2, 3, 7:15]`.
- Payload beat 4/code 1233 and `last=1` are held on cycles 4–7.
- Accepted boundary beat ordinals: `[4, 8, 12]`.
- Receiver packet lengths: `[4, 4, 4]` beats.
- Completion: cycle 15; 12 beats accepted once and in order.
- Active-window transfer rate: `12/15 = 0.8` beats/cycle.

The first packet closes on cycle 7, when its held last beat is accepted—not on cycle 4, when it is
first offered.

## Two independent levers

1. **Packet length, 2, 3, 4, or 6 beats/packet:** consumer readiness and all 12 payload words stay
   fixed. Packet count becomes `[6, 4, 3, 2]`, boundary density is `1/L` boundaries/beat, and
   completion remains cycle 15.
2. **Consumer ready-low duration, 0–6 cycles:** packet length stays four beats. Completion moves from
   cycles 12–18 and finite-window transfer rate becomes `12/(12+stall)` beats/cycle. Accepted
   boundaries remain `[4, 8, 12]` and all three packets remain four beats long.

The first lever changes grouping; the second changes timing. Reset one before moving the other so
the visible cause remains identifiable.

## Deliberately broken case

The broken source advances its `last` counter on every valid clock even when `ready=0`, while the
payload correctly holds. During the three-cycle baseline stall, boundary state advances three times
without an accepted payload beat.

All 12 payloads still arrive once and in order, but accepted `last` markers move from payload beats
`[4, 8, 12]` to `[5, 9]`. The receiver closes packets of five and four beats and retains an
unterminated three-beat tail. Five accepted beats disagree with their expected boundary metadata.
This is the central diagnostic: payload conservation does not prove packet integrity.

If erroneous drift equals a whole packet length, accepted boundaries can realign even though the
source changed `last` during a stall. Check both the hold obligation and receiver-visible framing;
a plausible packet count alone is not proof of protocol correctness.

## Learning flow

1. Read the transfer, boundary, and whole-beat hold rules; make one prediction about the stalled
   first boundary.
2. Run `lesson.m` or reveal `experiment.m` one `%%` section at a time.
3. Observe handshake state, held payload identity, held `last`, and receiver packet assignment.
4. Move only packet length, inspect the changed grouping, then read the mechanism and reset.
5. Move only consumer stall duration, inspect changed timing, then explain why boundaries remain.
6. Enable the broken boundary counter and locate the exact framing error despite intact payloads.
7. Run `interactive`, `run_checks`, answer `checks.md` one prompt at a time, and give the two-sentence
   teach-back.

## Files

- `model.m` — presentation-free deterministic handshake, boundary, and receiver accounting.
- `experiment.m` — baseline, two isolated sweeps, labeled metrics, and deliberate fault.
- `interactive.m` — bounded packet length, stall, observation-cycle, and fault controls.
- `lesson.m`, `lesson.md`, and `walkthrough.md` — learner and tutor sequence.
- `run_checks.m` and `checks.md` — invariants, limits, malformed inputs, recovery, and teach-back.

## Evidence boundary

The repository retains a bounded source model, executable MATLAB check source, and an independent
Python oracle used by static CI. No MATLAB or UI runtime was available for this batch, so figure
rendering, callbacks, and MATLAB numerical execution remain unvalidated. The model is a generic
single-clock valid/ready stream, not an AXI-Stream compliance model. It omits headers, explicit
length fields, CRC/FCS, partial-byte qualifiers, empty packets, reset, FIFO storage and sizing,
arbitration, timeout or cancellation policy, clock-domain crossing, metastability, HDL, synthesis,
placement, routing, and measured throughput. P12 addresses rate-based FIFO sizing; P18 later applies
streaming concepts to AXI-Stream. Bench, HIL, field, deployment, and production behavior require
separate retained evidence.
